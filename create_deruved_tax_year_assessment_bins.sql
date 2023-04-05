CREATE EXTENSION postgis;

CREATE OR REPLACE EXTERNAL TABLE `derived.tax_year_assessment_bins` (
    tax_year INTEGER,
    lower_bound INTEGER,
    upper_bound INTEGER,
    property_count INTEGER
)
OPTIONS (
    sourceUris = ['x'],
    format = 'CSV'
)

-- On line 10 we're unsure of what to use for sourceUris. X is a placeholder for now
	

