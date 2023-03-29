import csv
import io
import json
from google.cloud import storage
import functions_framework

@functions_framework.http
def prepare_data(request):
    client = storage.Client()
    raw_bucket = client.bucket(#'mjumbewu_musa_509_raw_data') # update
    processed_bucket = client.bucket(#'mjumbewu_musa_509_processed_data') # update

    raw_blob = raw_bucket.blob('opa/opa_properties.json')
    content = raw_blob.download_as_string()
    data = json.loads(content)

    processed_blob = processed_bucket.blob('opa_properties/data.csv')
    outfile = io.StringIO()
    writer = csv.writer(outfile)
    writer.writerows(data)
    processed_blob.upload_from_string(outfile.getvalue(), content_type='text/csv')

    return 'OK'
