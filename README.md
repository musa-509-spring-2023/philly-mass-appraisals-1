# Philadelphia Computer-Assisted Mass Appraisal (CAMA) Project

The following is a description of the various infrastructural components of the project. **The names and schemas used here are important, as each team will be working on different components of the project. The names and schemas are designed to be consistent across teams, so that the various components can be integrated together.** If you have any questions about the names or schemas, please ask!

The overview slides for the project are available [here](https://docs.google.com/presentation/d/1QZ6gXKYuN3Uk1owGHLrKVhh0EbPUGKQf9-VEnpnaCE4/edit?usp=sharing).

## Cloud Storage Buckets

Since bucket names must be globally unique, each name contains `team<N>` which should be replace with the actual team number (i.e., `team1` for orange, and `team2` for purple). The buckets are organized as follows:

| Bucket name | Description of contents |
|-------------|-------------------------|
| `musa509s23_team<N>_raw_data` | Raw data from the sources. |
| `musa509s23_team<N>_prepared_data` | Data prepared for external tables in BigQuery. |
| `musa509s23_team<N>_public` | Files that are accessible to the public. These files are primarily inteded to be consumed by the assessment review and property information apps. |

### Raw Data

In the `musa509s23_team<N>_raw_data` bucket, there are three folders. Each folder may contain one or multiple files, depending on the type of data loaded (for example, a shapefile may be stored as multiple files). The folders are as follows:

| Folder | Contents |
|--------|----------|
| `/opa_properties/` | Contains the "properties" data downloaded from the [Philadelphia Properties and Assessment History](https://opendataphilly.org/dataset/opa-property-assessments) dataset on OpenDataPhilly. |
| `/opa_assessments/` | Contains the "property assessment history" data downloaded from the [Philadelphia Properties and Assessment History](https://opendataphilly.org/dataset/opa-property-assessments) dataset on OpenDataPhilly. |
| `/pwd_parcels/` | Contains the "PWD parcels" data downloaded from the [PWD Stormwater Billing Parcels](https://opendataphilly.org/dataset/pwd-stormwater-billing-parcels) dataset on OpenDataPhilly. |

### Prepared Data

In the `musa509s23_team<N>_prepared_data` bucket, there are three folders. Each should contain a single file named `data.jsonl`. The folders are as follows:

| Folder | Contents |
|--------|----------|
| `/opa_properties/` | Contains the "properties" data prepared for external tables in BigQuery. |
| `/opa_assessments/` | Contains the "property assessment history" data prepared for external tables in BigQuery. |
| `/pwd_parcels/` | Contains the "PWD parcels" data prepared for external tables in BigQuery. |

### Public Files

The `musa509s23_team<N>_public` bucket contains files that are formatted to be used in the assessment review dashboard. These files are accessible via public URLs. Files used in this way (as artifacts for a web application) are often called "assets".

| Folder | Contents |
|--------|----------|
| `/tiles/` | Map tiles for the assessment reviewer
| `/configs/` | Configuration files for the charts and other parts of the assessment reviewer interface.

## BigQuery

### Datasets

| Dataset | Description |
|---------|-------------|
| `source` | External tables backed by prepared source data in Cloud Storage. |
| `core` | Data that is ready to be used for analysis. For the most part, the tables here are just copies of the external tables. |
| `derived` | Data that has been derived from core data. Outputs from analyses or models go here. |

### Tables

#### Source Tables

The tables in `source` are external tables. The data is stored in JSON-L files in the `musa509s23_team<N>_prepared_data` Cloud Storage bucket.

- `source.opa_properties`
- `source.opa_assessments`
- `source.pwd_parcels`

#### Core Tables

There's a correlated table in `core` for each table in `source`. Even though external tables are convenient for getting data into BigQuery, they're not the most efficient to query from. So, we copy the data into a table in `core` and query from there.

In addition to the fields from the raw tables, each of the core tables will have a `property_id` field (derived from the OPA or BRT number) that can be used as the unique identifier for a property across the tables.

- `core.opa_properties`
- `core.opa_assessments`
- `core.pwd_parcels`

#### Derived Tables

The `derived` schema contains all-new tables with data based on analyses and predictions. Below, each table is listed with the _minimal_ fields to include. The tables may have more fields than these (e.g., for `current_assessments` we may choose to store confidence interval data), but they will definitely have _at least_ the listed fields.

- `derived.tax_year_assessment_bins` -- The bins used to create the assessment distribution chart for a given tax year.
  
  *Minimal fields:*
  - `tax_year`
  - `lower_bound`
  - `upper_bound`
  - `property_count`

- `derived.current_assessment_bins` -- The bins used to create the distribution chart for the values generated by the assessment model.
  
  *Minimal fields:*
  - `lower_bound`
  - `upper_bound`
  - `property_count`

- `derived.property_tile_info` -- The information needed to generate map tiles for the assessment review dashboard.

  *Minimal fields:*
  - `property_id`
  - `address`
  - `geog`
  - `current_assessed_value` (as predicted by the model in the `derived.current_assessments` table)
  - `tax_year_assessed_value` (during the most recent tax year in the `core.opa_assessments` table)

- `derived.assessment_inputs` -- The inputs used to predict the current assessment value for each property.

  *Minimal fields:*
  - `property_id`
  - Whatever other fields are needed to make predictions...

- `derived.tax_year_assessments` -- The assessment values for each property for each tax year.

  *Minimal fields:*
  - `tax_year`
  - `property_id`
  - `assessed_value`

- `derived.current_assessments` -- The current assessment values for each property as predicted by the model.

  *Minimal fields:*
  - `property_id`
  - `assessed_value`



## Cloud Functions

### Extracting

Each of these tasks download data from some source and store the data in `musa509s23_team<N>_raw_data`.

- `extract-opa-properties`
- `extract-opa-assessments`
- `extract-pwd-parcels`

### Preparing (i.e. little-t transforming)

Each of these tasks read raw stored data from GCS and converts it into a clean CSV file in `musa509s23_team<N>_prepared_data`.

- `prepare-opa-properties`
- `prepare-opa-assessments`
- `prepare-pwd-parcels`

### Loading

Each of these creates (or replaces) an external table in the `source` dataset in BigQuery, and creates or replaces a copy of that data in the `core` dataset.

- `load-opa-properties`
- `load-opa-assessments`
- `load-pwd-parcels`

### Generating assets

- `generate-property-map-tiles`
- `generate-assessment-chart-configs`

## Cloud Run jobs

To run the assessment prediction across all the properties, we use a Cloud Run job named `predict-current-assessments`. The script reads the `derived.assessment_inputs` table and writes the results to the `derived.current_assessments` table.

## Workflows

For extracting, loading, transforming, and predicting on data, there is a single workflow named `data-pipeline`. This workflow is triggered by a Cloud Scheduler job that runs once per week.

## Service Accounts

In each project, a service account named `data-pipeline-user` was created to provide necessary access to different GCP services. The following roles are assigned to the service account:

- `Storage Object Admin`
- `BigQuery Job User`
- `Cloud Functions Invoker`
- `Cloud Run Invoker`
- `Workflows Invoker`
