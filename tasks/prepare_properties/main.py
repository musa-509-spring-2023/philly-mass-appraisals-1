import json
from google.cloud import storage
import functions_framework

@functions_framework.http
def prepare_data(request):
    client = storage.Client()
    raw_bucket = client.bucket('musa509s23_team01_raw_data') # update
    processed_bucket = client.bucket('musa509s23_team01_prepared_data') # update

    raw_blob = raw_bucket.blob('phl_opa_properties/opa_properties.json')
    content = raw_blob.download_as_string()
    data = json.loads(content)

    rows = []
    for feature in data['features']:
        row = feature['properties']
        row['geog'] = json.dumps(feature['geometry'])
        rows.append(json.dumps(row))

    processed_blob = processed_bucket.blob('opa_properties/data.jsonl')
    processed_blob.upload_from_string('\n'.join(rows), content_type='application/jsonl')

    return 'OK'
