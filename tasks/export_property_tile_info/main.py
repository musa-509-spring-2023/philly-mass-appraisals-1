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
def export_temp_data(request):
    bigquery_client = bigquery.Client()
    project_id = os.environ['GCP_PROJECT']
    dataset_id = 'derived'

    storage_client = storage.Client()
    bucket_name = 'musa509s23_team01_temp_data'
    bucket = storage_client.bucket(bucket_name)

    # Convert table rows to GeoJSON features
    table_id = 'property_tile_info'
    query = f'''
        SELECT * FROM {project_id}.{dataset_id}.{table_id}
    '''
    query_job = bigquery_client.query(query)
    rows = query_job.result()

    features = []
    for row in rows:
        feature = {
            'type': 'Feature',
            'properties': {
                attr: val
                for attr, val in row.items()
                if attr != 'geog_json'
            },
            'geometry': json.loads(row['geog_json'])
        }
        features.append(feature)
    json_data = json.dumps({
        'type': 'FeatureCollection',
        'features': features
    }, cls=MoneyEncoder)

    blob = bucket.blob('property_tile_info.geojson')
    blob.upload_from_string(json_data, content_type='application/json')

    return 'GeoJSON file generated and uploaded to Cloud Storage', 200


if __name__ == '__main__':
    export_temp_data('test')
