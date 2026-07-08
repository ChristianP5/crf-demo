from datetime import datetime
from google.cloud import storage
import functions_framework
import os
import tempfile

DESTINATION_BUCKET_NAME = "c-lab59-destination-bucket"

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def upload_on_upload_bucket_function(cloud_event):
    data = cloud_event.data

    # Extract Information about the Triggering Bucket and Blob
    source_bucket_name = data["bucket"]
    source_blob_name = data["name"]

    # Generate a File Name for the Downloaded Blob
    destination_blob_name = generateFileName(source_blob_name)

    # Create a Temporary File to Download the Blob
    download_blob(source_bucket_name,source_blob_name, destination_blob_name)


    # Upload the Temporary File to the Destination Bucket
    source_file_name = destination_blob_name
    destination_bucket_name = DESTINATION_BUCKET_NAME
    destination_blob_name = source_file_name
    upload_file(source_file_name,destination_bucket_name, destination_blob_name)


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


def download_blob(source_bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(source_bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, source_bucket_name, destination_file_name
        )
    )

def upload_file(source_file_name, destination_bucket_name, destination_blob_name):
    """Upload a blob from the bucket."""
    # Upload result to a second bucket, to avoid re-triggering the function.
    # You could instead re-upload it to the same bucket + tell your function
    # to ignore files marked as blurred (e.g. those with a "blurred" prefix)

    storage_client = storage.Client()

    destination_bucket = storage_client.bucket(destination_bucket_name)
    new_blob = destination_bucket.blob(destination_blob_name)
    new_blob.upload_from_filename(source_file_name)
    print(f"{source_file_name} File uploaded to: gs://{destination_bucket_name}/{destination_blob_name}")

    # Delete the temporary file.
    os.remove(source_file_name)
