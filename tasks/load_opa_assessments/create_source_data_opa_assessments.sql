CREATE OR REPLACE EXTERNAL TABLE `source.opa_assessments` (
    'exempt_building' STRING,
    'exempt_land' STRING,
    'market_value' STRING,
    'parcel_number' STRING,
    'taxable_building' STRING,
    'taxable_land' STRING,
    'year' STRING
)
OPTIONS (
    uris = ['gs://musa509s23_team01_prepared_data/opa_assessments/data.jsonl'],
    format = 'JSON'
)