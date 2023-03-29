import json
import requests
from google.cloud import storage
import functions_framework

@functions_framework.http
def extract_data(request):
    client = storage.Client()
    bucket = client.bucket(musa509spring2023_raw_data) # update bucket 'mjumbewu_musa_509_raw_data')

    url = 'https://opendata-downloads.s3.amazonaws.com/assessments.csv'
    resp = requests.get(url)
    data = resp.json()

    json_data = json.dumps(data)
    blob = bucket.blob('phl_opa_properties/assessment_histories.json') #check this is right
    blob.upload_from_string(json_data, content_type='application/json')

    return 'OK'
