import pathlib
from google.cloud import bigquery
import functions_framework

DIR = pathlib.Path(__file__).parent

@functions_framework.http
def load_data(request):
    client = bigquery.Client()

    with open(DIR / 'create_source_data_opa_properties.sql') as f:
        sql = f.read()
    job = client.query(sql)
    job.result()

    with open(DIR / 'create_internal_table_opa_properties.sql') as f:
        sql = f.read()
    job = client.query(sql)
    job.result()

    return 'OK'
