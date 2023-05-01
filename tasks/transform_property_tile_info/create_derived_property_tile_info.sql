CREATE OR REPLACE TABLE `derived.property_tile_info` AS

WITH `latest_tax_year` AS (
    SELECT MAX(`year`) AS `year`
    FROM `core.opa_assessments`
)

SELECT
    curr.`property_id`,
    parcels.`address`,
    ST_ASGEOJSON(parcels.`geog`) AS `geog_json`,
    curr.`assessed_value` AS `current_assessed_value`,
    past.`market_value` AS `tax_year_assessed_value`
FROM `derived.current_assessments` AS curr
INNER JOIN `core.pwd_parcels` AS parcels USING (`property_id`)
LEFT JOIN `core.opa_assessments` AS past USING (`property_id`)
CROSS JOIN `latest_tax_year`
WHERE
    past.`property_id` IS NULL
    OR past.`year` = `latest_tax_year`.`year`
