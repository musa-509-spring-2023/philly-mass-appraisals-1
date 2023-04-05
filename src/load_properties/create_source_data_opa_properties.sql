CREATE OR REPLACE EXTERNAL TABLE `source.opa_properties` (
    -- name STRING,
    -- geoid STRING,
    -- population INTEGER,
    -- state STRING,
    -- county STRING,
    -- tract STRING,
    -- block_group STRING
)
OPTIONS (
    sourceUris = ['gs://musa509s23_team01_prepared_data/phl_opa_properties/opa_properties.jsonl'],
    format = 'JSON'
)