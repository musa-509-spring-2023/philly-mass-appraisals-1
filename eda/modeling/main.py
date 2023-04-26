import carto2gpd
import geopandas as gpd
import pandas as pd
import numpy as np
import hvplot.pandas
import datetime as dt
import matplotlib.pyplot as plt
from census import Census
from us import states
import os
import seaborn as sns


## Load sklearn dependencies

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Model selection
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV

# Pipelines
from sklearn.pipeline import make_pipeline

# Preprocessing
from sklearn.preprocessing import StandardScaler, PolynomialFeatures

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from sklearn.neighbors import NearestNeighbors



@functions_framework.http
def model():

    ### HB & SNOW
    
    #Pull in data from cloud storage & cut down to mannageable size
    #Filter it for assessment date and zoning

    #Pull data from OPA --> should be querying from BigQuery/Cloud Storage
    carto_url = "https://phl.carto.com/api/v2/sql"

    table_name = "opa_properties_public"

    #filter for Zoned Residential
    where = "assessment_date >= '2022-01-01' and assessment_date <= '2023-04-01'"
    where = where + " and zoning LIKE 'R%'"

    opaRaw = carto2gpd.get(carto_url, table_name, where=where)

    ### DONE HB & SNOW

    #Get tracts/neighborhoods for geodata
    tracts = gpd.read_file('https://opendata.arcgis.com/datasets/8bc0786524a4486bb3cf0f9862ad0fbf_0.geojson')
    neighborhoods = gpd.read_file('https://raw.githubusercontent.com/azavea/geo-data/master/Neighborhoods_Philadelphia/Neighborhoods_Philadelphia.geojson')

    #Spatially join tracts, neighborhoods, and properties

    opa1 = opaRaw.sjoin(tracts,how="left")
    opa1 = opa1.drop(["index_right"], axis=1)
    opa1 = opa1.sjoin(neighborhoods, how="left")

    pd.set_option('display.max_columns', None)
    opa1.sort_values('taxable_land').head()

    #Select columns

    cols = ["market_value", #Num
            "sale_price", #Num
        "total_livable_area", #Num
        "total_area", #Num
        "garage_spaces", #Num
        "fireplaces", #Num
        "number_of_bathrooms", #Num
        "number_of_bedrooms",  #Num
        "number_stories",  #Num
        "central_air", #Cat
        "exterior_condition", #Cat
        "zip_code", #Cat
            "homestead_exemption", #Int --> #Cat
            "year_built", #Cat
            "zoning", #Cat
            "GEOID10", #Cat
            "name", #Cat
            "interior_condition",
            'geometry'
        ]

    #Select only some columns
    opa = opa1[cols].copy()

    count = opa['market_value'].value_counts().get(0, 0)
    length = len(opa)
    div = round(count/length * 100,2)
    print(f"Number of rows with zero value: {count} out of {length} values ({div}%)")

    max_m = opa['market_value'].max()
    mean_m = opa['market_value'].mean()
    median_m = opa['market_value'].median()

    print(f"Max market value: {max_m}")
    print(f"Mean: {mean_m}")
    print(f"Median: {median_m}")

    #Fix some categorical variables
    opa["homestead_exemption"] = np.where(opa["homestead_exemption"] > 0, "T", "F")
    opa["central_air"] = np.where((opa["central_air"] == "0") | (opa["central_air"] == "1"),
                                "F", "T")
    opa["year_built"] = pd.to_numeric(opa["year_built"])
    opa = opa.dropna(subset=['market_value', 
                            'geometry', 
                            "total_area",
                            "number_of_bathrooms",
                            "number_of_bedrooms",
                            "number_stories",
                            "year_built"])

    # Identify sale prices of nearest neighbors

    from sklearn.neighbors import NearestNeighbors

    def get_xy_from_geometry(df):
        """
        Return a numpy array with two columns, where the 
        first holds the `x` geometry coordinate and the second 
        column holds the `y` geometry coordinate
        
        Note: this works with both Point() and Polygon() objects.
        """
        # NEW: use the centroid.x and centroid.y to support Polygon() and Point() geometries 
        x = df.geometry.centroid.x
        y = df.geometry.centroid.y
        
        return np.column_stack((x, y)) # stack as columns

    # Convert to meters and EPSG=3857
    opa_3857 = opa.to_crs(epsg=3857)

    # Extract x/y for sales
    opaXY = get_xy_from_geometry(opa_3857)

    N = 5
    k = N + 1
    nbrs = NearestNeighbors(n_neighbors=k)
    nbrs.fit(opaXY)

    opaDists, opaIndices = nbrs.kneighbors(opaXY)

    # Handle any locations that have 0 distances
    opaDists[opaDists == 0] = 1e-5 

    opa["logOPADists"] = np.log10(opaDists[:, 1:].mean(axis=1))

    total_opa = opa['sale_price'].values

    neighboring_opa = total_opa[opaIndices[:, 1:]]

    opa['laggedOPA'] = neighboring_opa.mean(axis=1)

    #Get Census data

    # Set the API
    c = Census(os.environ.get("CENSUS_API_KEY"))

    # Set the fields
    fields = ("NAME", 'B19013_001E', 'B03002_001E')

    # Get the Philadelphia County Census data
    pa_census = c.acs5.state_county_tract(fields, state_fips="42", county_fips="101", tract="*", year=2020)
    pa_census_df = pd.DataFrame(pa_census)
    pa_df = pd.DataFrame(pa_census)
    pa_df 

    pa_df["GEOID"] = pa_df["state"] + pa_df["county"] + pa_df["tract"]

    # Merge the census data
    opa = opa.merge(pa_df, left_on="GEOID10", right_on="GEOID", how="left")

    opa.rename(columns={'B19013_001E': 'median_income'}, inplace=True)

    #remove columns with NaN values
    opa = opa.dropna()

    # Add in the lagged OPA and Census data to model

    #Add in categorical

    num_cols = [
        "total_livable_area",
        "total_area",
        "number_of_bathrooms",
        "number_of_bedrooms",
        "number_stories",
        "year_built",
        "laggedOPA",
        "median_income"]

    #Categorical columns
    cat_cols = ["central_air", 
        "exterior_condition", 
        "interior_condition", 
        "homestead_exemption", 
        "zoning", 
        "name" 
            ]

    transformer = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )

    # Split the data 70/30
    train_set, test_set = train_test_split(opa, 
                                        test_size=0.3, 
                                        random_state=42)

    # the target labels: log of sale price
    y_train = np.log(train_set["market_value"])
    y_test = np.log(test_set["market_value"])

    pipe = make_pipeline(
        transformer, RandomForestRegressor(n_estimators=500, 
                                        random_state=42))


    # Fit the training set
    pipe.fit(train_set, y_train)

    # What's the test score?
    pipe.score(test_set, y_test)
