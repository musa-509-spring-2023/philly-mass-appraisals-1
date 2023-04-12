# Discussion About Data Source
We are using the OPA dataset from Open Data Philly and pulling in information from outside sources.

The information we need to predict: property tax assessment = taxable land + taxable building

Both Haobing and Lizzie used this dataset last semester to predict market values. We will be using similar information and methods to predict property tax assessment values instead.

## OPA Fields

These are the fields we plan to use from the OPA dataset:

    "market_value", #Num
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
    "homestead_exemption", #Int --> #Cat; whether or not this is a homeowner's residence
    "year_built", #Cat
    "zoning", #Cat
    "GEOID10", #Cat
    "name", #Cat
    "interior_condition",
    'geometry'

### Exploring this data
Taxable land and building were misleading fields -- many were zero when the market_value (and "assessed value" on the Atlas site) was non-zero. We will be using 'market_value' as our dependent variable. 

A very small percentage of properties have a zero value for 'market_value.'

Max market value: 276,892,000
Mean: 450378.55
Median: 229700.0


## Additional Feature Engineering

### Census Data
We will spatially merge the OPA dataset with Census data to get the block group information for each parcel. We will then include Census data on median household income and race/ethnicity.

### Spatial Lag
Looking at the values of 10 nearest neighbors. This point assumes that the assessed values of neighbors correspond to assessed value of the property in question. 

### Crime 
Looking at crime incidents data from Open Data Philly - measure distance to nearest drug, homicide, receiving stolen property, and vagrancy arrests. This point assumes that the closer a building is located to one of these crimes, the lower its assessed value would be.

### 311: Escalation to L&I
Looking at 311 data for complaints that escalate building inspection complaints to L&I -- something we assume would correlate with lower assessed values.

### 311: Illegal Dumping Complaints
Looking at 311 data for complaints about illegal dumping -- something we assume would correlate with lower assessed values.

### Nearby amenities
Looking to Open Street Maps data on distance to nearest universities, coffee shops, and/or hospitals -- we assume shorter distances would correlate with higher assessed values.