# The python code for cloud function (Task 08)

import os
import pathlib
import functions_framework
from google.cloud import bigquery

ROOT = pathlib.Path(__file__).parent


@functions_framework.http
def generate_derived_table(request):
    project_id = os.environ['GCP_PROJECT']

    # Read the SQL query from the file
    with open(ROOT / 'create_derived_property_tile_info.sql', 'r') as sql_file:
        sql_query = sql_file.read()

    # Run the SQL query
    client = bigquery.Client(project=project_id)
    query_job = client.query(sql_query)
    query_job.result()

    return 'Table generated successfully', 200
