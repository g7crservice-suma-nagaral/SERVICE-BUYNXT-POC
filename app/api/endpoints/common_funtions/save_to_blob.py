from datetime import datetime
import json
import os
from azure.storage.blob import BlobServiceClient
from fastapi import HTTPException

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
OUTPUT_CONTAINER_NAME = os.getenv("OUTPUT_CONTAINER_NAME")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER_NAME)


def make_serializable(data):
    """
    Recursively convert non-serializable objects into JSON-compatible types.
    """
    if isinstance(data, dict):
        return {key: make_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [make_serializable(item) for item in data]
    elif hasattr(data, '__dict__'):
        return make_serializable(data.__dict__)
    elif isinstance(data, (str, int, float, bool)) or data is None:
        return data
    else:
        return str(data)  # Fallback to string representation for unsupported types


#Function to store the output file to Blob
async def save_to_blob_storage(data: dict, file_name: str) -> str:
    """
    Save processed data to Azure Blob Storage with the original file name and timestamp.
    - **data:** JSON serializable data to be saved.
    - **file_name:** Original file name from the uploaded file.
    """
    try:
        # current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        file_base, _ = os.path.splitext(file_name)
        # blob_name = f"{file_base}_{current_time}.json"
        blob_name = f"{file_base}.json"

        blob_client = container_client.get_blob_client(blob_name)

        serializable_data = make_serializable(data)
        blob_client.upload_blob(json.dumps(serializable_data), overwrite=True)

        blob_url = f"{blob_service_client.url}/{OUTPUT_CONTAINER_NAME}/{blob_name}"
        return blob_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to Blob Storage: {str(e)}")

