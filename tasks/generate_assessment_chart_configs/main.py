import decimal
import json
import os
import pathlib
import functions_framework
from google.cloud import bigquery
from google.cloud import storage

ROOT = pathlib.Path(__file__).parent


class MoneyEncoder(json.JSONEncoder):
    """
    JSON encoder to convert a decimal.Decimal object to a string when encoding.
    This is necessary because lower and upper bounds on bins will use the
    Decimal type (instead of int or float), and the default Python JSON encoder
    does not know how to handle this type.
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return round(float(o), 2)
        return super().encode(o)


@functions_framework.http
def generate_assessment_chart_configs(request):
    bigquery_client = bigquery.Client()
    project_id = os.environ['GCP_PROJECT']
    dataset_id = 'derived'

    storage_client = storage.Client()
    bucket_name = 'musa509s23_team01_public'
    bucket = storage_client.bucket(bucket_name)

    # Generate the tax year assessment bins file
    table_id = 'tax_year_assessment_bins'
    query = f'SELECT * FROM {project_id}.{dataset_id}.{table_id}'
    query_job = bigquery_client.query(query)
    rows = query_job.result()

    results = []
    for row in rows:
        if len(results) < 10:
            print(row)
        results.append({
            'tax_year': row['tax_year'],
            'lower_bound': row['lower_bound'],
            'upper_bound': row['upper_bound'],
            'property_count': row['number_properties']
        })
    json_data = json.dumps(results, cls=MoneyEncoder)

    blob = bucket.blob('configs/tax_year_assessment_bins.json')
    blob.upload_from_string(json_data, content_type='application/json')

    # Generate the current (predicted) assessment bins file
    table_id = 'current_assessment_bins'
    query = f'SELECT * FROM {project_id}.{dataset_id}.{table_id}'
    query_job = bigquery_client.query(query)
    rows = query_job.result()

    results = []
    for row in rows:
        if len(results) < 10:
            print(row)
        results.append({
            'lower_bound': row['lower_bound'],
            'upper_bound': row['upper_bound'],
            'property_count': row['number_properties']
        })
    json_data = json.dumps(results, cls=MoneyEncoder)

    blob = bucket.blob('configs/current_assessment_bins.json')
    blob.upload_from_string(json_data, content_type='application/json')

    return 'JSON files generated and uploaded to Cloud Storage', 200
