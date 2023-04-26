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
import functions_framework


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


# Get the data from Google Cloud buckets
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/ejs/philly-mass-appraisals-1/eda/keys/musa509s23-team1-philly-cama-b413417455db.json"

# Set the environment variable with the path to your JSON key file
# Define the bucket and file path
bucket_name = "musa509s23_team01_raw_data"
file_path = "phl_opa_properties/opa_properties.json"

# Define the function to get the data from Google Cloud buckets
def get_blob_string(bucket_name, source_blob_name):
    """Reads a blob from the bucket as a string."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    return blob.download_as_text()
# Read the data as a string
data_string = get_blob_string(bucket_name, file_path)
# Create a DataFrame from the string
data_df = pd.read_json(StringIO(data_string))

# Convert the GeoJSON file into dataframe
import json
# Load the GeoJSON data
geojson_data = json.loads(data_string)
features = geojson_data["features"]
# Extract the properties of each feature and create a new list of dictionaries
properties_list = [feature["properties"] for feature in features]
# Create a DataFrame from the list of dictionaries
opaRaw = pd.DataFrame(properties_list)
opaFilt = opaRaw.loc[(opaRaw['assessment_date'] >= '2022-01-01') & (opaRaw['assessment_date'] <= '2023-04-01') & (opaRaw['zoning'].str.startswith('R'))]


@functions_framework.http
def model():

    #Get tracts/neighborhoods for geodata
    tracts = gpd.read_file('https://opendata.arcgis.com/datasets/8bc0786524a4486bb3cf0f9862ad0fbf_0.geojson')
    neighborhoods = gpd.read_file('https://raw.githubusercontent.com/azavea/geo-data/master/Neighborhoods_Philadelphia/Neighborhoods_Philadelphia.geojson')

    #Spatially join tracts, neighborhoods, and properties

    opa1 = opaFilt.sjoin(tracts,how="left")
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

#Still more to do to actually make predictions...
