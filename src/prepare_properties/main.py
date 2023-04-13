import csv
import io
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

    processed_blob = processed_bucket.blob('opa_properties/data.jsonl')
    #outfile = io.StringIO()
    #writer = csv.writer(outfile) # convert to jsonl
    #writer.writerows(data)
    with open('opa_properties.jsonl', 'w', encoding='utf-8') as f:
        for feature in data['features']:
            row = feature['properties']
            row['geog'] = json.dumps(feature['geometry'])
            f.write(json.dumps(row) + '\n')
        processed_blob.upload_from_file(f)

    return 'OK'

####
# import json

# # Load the data from the GeoJSON file
# with open('opa_properties_public.geojson', 'rU', encoding='utf-8', errors = 'ignore') as f:
#     data = json.load(f)

# # Write the data to a JSONL file
# with open('opa_properties.jsonl', 'w', encoding='utf-8') as f:
#     for feature in data['features']:
#         row = feature['properties']
#         row['geog'] = json.dumps(feature['geometry'])
#         f.write(json.dumps(row) + '\n')