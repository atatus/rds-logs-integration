import json
import gzip
import boto3 
import requests
import shlex
from datetime import datetime

s3 = boto3.client('s3')

bucket_name = '<YOUR_BUCKET_NAME>'
atatus_log_ingest_endpoint = 'https://api.atatus.com/track/logs/ingest'
atatus_api_key = '<YOUR_API_KEY>'
atatus_source = 'rds-source'
atatus_service = 'rds-service'

def validate_timestamp(timestamp, format="%Y-%m-%dT%H:%M:%S.%fZ"):
    try:
        datetime_obj = datetime.strptime(timestamp, format)
        return True
    except ValueError:
        return False

def convert_log_line_to_json(line):
    
    if not line.strip():
        return None 
        
    res = shlex.split(line, posix=False)

    is_valid = validate_timestamp(res[0])

    if is_valid:
        res[0] = res[0]
    else:
        formatted_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        formatted_timestamp = formatted_timestamp[:-3] + 'Z'

        res[0] = formatted_timestamp

    rds_headers = ['timestamp', 'message', 'source', 'service']
    res= [res[0], line, atatus_source, atatus_service]

    return dict(zip(rds_headers, res))

def lambda_handler(event, context):

    response = s3.list_objects_v2(Bucket=bucket_name)

    if "Contents" in response:
        # Sort objects by LastModified in descending order
        sorted_objects = sorted(response['Contents'], key=lambda obj: obj['LastModified'], reverse=True)

        # Get the latest log file
        latest_log_file = sorted_objects[0]

        file_key = latest_log_file['Key']

        if file_key.endswith('.gz'):
            file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
            file_content = file_obj['Body'].read()

            # Decompress the gzipped content
            decompressed_content = gzip.decompress(file_content)

            # Convert bytes to string
            json_data = str(decompressed_content, encoding='utf-8')

            # Split the string into lines
            lines = json_data.strip().split('\n')
        
            # Convert the list of strings into a JSON-formatted string
            result = json.dumps(lines, indent=4)
            
            # Load the JSON-formatted string into a list of strings
            list_of_strings = json.loads(result)

            # Convert each log line string into a JSON object
            # json_data = [convert_log_line_to_json(line) for line in list_of_strings]
            json_data = [json_obj for line in list_of_strings if (json_obj := convert_log_line_to_json(line)) is not None]

            req_headers = {
                'x-api-key': atatus_api_key,
                'Content-Type': 'application/json'
            }

            # Send the JSON data to the specified HTTP endpoint
            response = requests.post(atatus_log_ingest_endpoint, json=json_data, headers=req_headers)

            print("response :", response)
            
            # Print information about the sent data and the response received
            print(f"Ingested Logs data to Atatus. Response: {response.status_code}")
        else:
            print("The latest file is not a gzipped log file.")