import json
import requests
from google.cloud import storage
import functions_framework
import dotenv
dotenv.load_dotenv()

@functions_framework.http
def extract_data(request):
    client = storage.Client()
    bucket = client.bucket('musa509s23_team01_raw_data')
    url = 'https://phl.carto.com/api/v2/sql?q=SELECT+*+FROM+assessments'
    resp = requests.get(url)
    json_data = resp.text
    blob = bucket.blob('phl_opa_assessments/opa_assessments.json')
    blob.upload_from_string(json_data, content_type='application/json')

    return 'OK'
