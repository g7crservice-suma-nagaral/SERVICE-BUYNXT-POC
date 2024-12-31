# FastAPI Endpoint
import asyncio
from datetime import datetime
import json
import os
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.model.category import PromptRequest,ProductResponse
from app.api.endpoints.prod_category import function
from app.core.dependency import check_api_key 
from azure.storage.blob import BlobServiceClient

app=APIRouter(tags=["Az AI Serices"])


AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
INPUT_CONTAINER_NAME = os.getenv("INPUT_CONTAINER_NAME")
OUTPUT_CONTAINER_NAME = os.getenv("OUTPUT_CONTAINER_NAME")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER_NAME)
input_container_client = blob_service_client.get_container_client(INPUT_CONTAINER_NAME)


@app.post("/generate-image/")
async def generate_image(request: PromptRequest,authorized: bool = Depends(check_api_key)):
    try:
        await asyncio.sleep(20)
        result = function.generate_image(request.prompt)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.get("/categorize-product/", response_model=ProductResponse)
async def categorize_product(product_name: str,authorized: bool = Depends(check_api_key)):
    try:
        await asyncio.sleep(10)
        result = function.categorize_product(product_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/extract-invoice-text")
async def extract_invoice_endpoint(file: UploadFile = File(...), authorized: bool = Depends(check_api_key)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Create a timestamped filename
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        file_base, file_extension = os.path.splitext(file.filename)
        blob_name = f"{file_base}_{current_time}{file_extension}"

        # Upload file to Blob Input Container
        blob_client = input_container_client.get_blob_client(blob_name)
        file_content = await file.read()
        blob_client.upload_blob(file_content, overwrite=True)
        blob_url = f"{blob_service_client.url}/{INPUT_CONTAINER_NAME}/{blob_name}"

        # Pass Blob URL to the processing function
        result = await function.extract_invoice_data_from_blob(blob_url)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
   
@app.get("/get_file_list")
def get_file_list(authorized: bool = Depends(check_api_key)):
    try:
        result = function.fn_get_file_list()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download_blob_file")
def download_blob_file(file_name: str):
    try:
        result = function.fn_download_file(file_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))