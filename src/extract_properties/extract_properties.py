import json
import requests
from google.cloud import storage
import functions_framework

@functions_framework.http
def extract_data(request):
    client = storage.Client()
    bucket = client.bucket('musa509spring2023_raw_data') # update bucket 'mjumbewu_musa_509_raw_data')

    url = 'https://phl.carto.com/api/v2/sql?filename=opa_properties_public&format=geojson&skipfields=cartodb_id&q=SELECT+*+FROM+opa_properties_public'
    resp = requests.get(url)
    data = resp.json()

    json_data = json.dumps(data)
    blob = bucket.blob('phl_opa_properties/opa_properties.json')
    blob.upload_from_string(json_data, content_type='application/json')

    return 'OK'
