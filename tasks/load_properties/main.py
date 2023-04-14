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




# import csv
# import io
# import json
# from google.cloud import storage
# import functions_framework

# @functions_framework.http
# def load_opa_properties(request):
#     client = storage.Client()
#     processed_bucket = client.bucket('musa509s23_team01_prepared_data')

#     processed_blob = processed_bucket.blob('opa_properties/data.jsonl')
#     content = processed_blob.download_as_string()

#     # create external table
