def generate_assessment_chart_configs(request):
project_id = os.environ['GCP_PROJECT']
dataset_id = 'derived'
table_id = 'current_assessment_bins'
client = bigquery.Client()
table_ref = client.dataset(dataset.id).table(table_id)
table = client.get_table(table_ref)
query = f'SELECT * FROM {project_id}.{dataset_id}.{table_id}'
query_job = client.query(query)
rows = query_job.result()
results = []
for row in rows:
results.append({
'tax_year': row['tax_year'],
'lower_bound': row['lower_bound'],
'upper_bound': row['upper_bound'],
'property_count': row['number_properties']
})
json_filename = 'tax_year_assessment_bins.json'
with open(json_filename, 'w') as f:
json.dump(results, f)
storage_client = storage.Client()
bucket_name = 'musa509s2023_team1_public'
bucket = storage_client.get_bucket(bucket_name)
blob = bucket.blob(f'configs/{tax_year_assessment_bins.json}')
blob.upload_from_filename(json_filename)
return 'JSON file generated and uplaoded to Cloud Storage', 200