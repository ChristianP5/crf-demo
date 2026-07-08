import functions_framework
from google.cloud import compute_v1
from google.cloud import storage
from datetime import datetime


@functions_framework.http
def start_vm_function(request):

    # Constants
    PROJECT_ID = "bsi-mlpt-training"
    BUCKET_ID = "clab59bucket"

    # Get a List VM Instances
    instances_list = list_instances()

    # Start the VM Instances
    result = start_instances(instances_list)

    return {
        "status" : "success",
        "data": {
            "execution_result": result
        }
    }

# List of VM Instances
# Output Format:
# [{"name": ..., "zone": ...,}]
#
def list_instances():
    # Create a client
    client = compute_v1.InstancesClient()

    # Initialize request argument(s)
    request = compute_v1.AggregatedListInstancesRequest(
        project=PROJECT_ID,
        filter='(labels.crf-vm-start = true) AND (status = TERMINATED)'
    )

    # Make the request
    response = client.aggregated_list(request=request)

    # Handle the response
    instances = []
    for zone, scoped_list in response:
        if scoped_list.instances:
            for instance in scoped_list.instances:
                instances.append({"name" : instance.name, "zone" : zone.split('/')[1]})
                
    return instances


# Upload Blob Function
def upload_blob(upload_string, destination_blob_name):
    """Uploads a file to the bucket."""
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_ID)
    blob = bucket.blob(destination_blob_name)

    result = blob.upload_from_string(upload_string)

    print(
        f"{destination_blob_name} created."
    )
    
    return result

# Generate File Name Function
# Output Example:
# start_execution_log-2026_07_08_15:04:09
#
def generateFileName(operation = "start"):
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
    
    blob_filename = f"{year}_{month}_{day}_{hour}:{minute}:{second}-{operation}_execution_log"
    print(blob_filename)
    return blob_filename

# Start VM Instances from List of VM Instances
def start_instances(instances_list):
    # Create a client
    client = compute_v1.InstancesClient()
    result = []
    execution_report = ""
    for instance in instances_list:
        # Initialize request argument(s)
        request = compute_v1.StartInstanceRequest(
            instance=instance["name"],
            project=PROJECT_ID,
            zone=instance["zone"],
        )

        # Make the request
        response = client.start(request=request)
        result.append(response)

        execution_report = execution_report + f"{instance["name"]} started successfully.\n"

    # Log the Execution
    upload_blob(execution_report,generateFileName("start"))
    
    # Handle the response
    return execution_report