CREATE OR REPLACE TABLE derived.tax_year_assessment_bins AS
SELECT 
  year, 
  FLOOR(market_value / 10000) * 10000 AS lower_bound, 
  FLOOR(market_value / 10000) * 10000 + 10000 AS upper_bound, 
  COUNT(*) number_properties
FROM `core.opa_assessments`
GROUP BY 1,2,3
ORDER BY 1,2
