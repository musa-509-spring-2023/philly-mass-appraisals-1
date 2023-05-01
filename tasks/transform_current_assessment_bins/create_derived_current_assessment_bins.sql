CREATE OR REPLACE TABLE
  derived.current_assessment_bins AS
SELECT
  FLOOR(assessed_value / 10000) * 10000 AS lower_bound,
  FLOOR(assessed_value / 10000) * 10000 + 10000 AS upper_bound,
  COUNT(*) number_properties
FROM
  `derived.current_assessments`
GROUP BY
  1,
  2
ORDER BY
  1,
  2
