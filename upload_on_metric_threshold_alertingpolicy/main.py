import base64
import json
import functions_framework
from flask import abort
from datetime import datetime
from google.cloud import storage
import os

DESTINATION_BUCKET_NAME = "c-lab59-destination-bucket"

@functions_framework.http
def upload_on_metric_threshold_alertingpolicy(request):
    request_json = request.get_json(silent=True)

    if request_json is None or 'message' not in request_json:
        abort(400, description="Bad Request: 'message' field is missing")

    message_json = request_json['message']

    if message_json is None or 'data' not in message_json:
        abort(400, description="Bad Request: Pub/Sub message or data field is missing")

    encoded_data = message_json['data']
    try:
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        payload_json = json.loads(decoded_data)

        # Extract information about the triggering incident
        incident = payload_json.get("incident", {})
        resource_display_name = incident.get("resource_display_name", "unknown")
        summary = incident.get("summary", "")

        payload = f"Resource: {resource_display_name}\nSummary: {summary}"
        print(f"Payload: {payload}")

        destination_blob_name = generateFileName("metric_threshold_alert.txt")
        upload_blob(payload, destination_blob_name)

        return "OK"
    except Exception as e:
        print(f"Error processing Pub/Sub message: {e}")
        abort(500, description="Error processing message")

def generateFileName(filename):
    now = str(datetime.now())
    
    print(now)
    
    year = now.split()[0].split("-")[0]
    month = now.split()[0].split("-")[1]
    day = now.split()[0].split("-")[2]
    hour = now.split()[1].split(":")[0]
    minute = now.split()[1].split(":")[1]
    second = now.split()[1].split(":")[2][:2]
    # print(f"Year: {year}")
    # print(f"Month: {month}")
    # print(f"Day: {day}")
    # print(f"Hour: {hour}")
    # print(f"Minute: {minute}")
    # print(f"second: {second}")
    
    blob_filename = f"{year}-{month}-{day}-{hour}_{minute}_{second}_{filename}"
    print(blob_filename)
    return blob_filename

def upload_blob(upload_string, destination_blob_name):
    """Uploads a file to the bucket."""
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(DESTINATION_BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    result = blob.upload_from_string(upload_string)

    print(
        f"{destination_blob_name} created."
    )
    
    return result