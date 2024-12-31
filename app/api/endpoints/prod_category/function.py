from datetime import datetime
import uuid
from fastapi import  HTTPException, File, UploadFile, HTTPException
import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import tempfile
from app.api.endpoints.common_funtions import save_to_blob, analyse_data
from azure.storage.blob import BlobServiceClient
from fastapi.responses import StreamingResponse

# Load environment variables
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_OPENAI_DEPLOYMENT_NAME_IMG = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_IMG")
AZURE_FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
AZURE_FORM_RECOGNIZER_KEY = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
INPUT_CONTAINER_NAME = os.getenv("INPUT_CONTAINER_NAME")
OUTPUT_CONTAINER_NAME = os.getenv("OUTPUT_CONTAINER_NAME")

# Initialize Azure OpenAI Client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION
)

# Azure Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER_NAME)
input_container_client = blob_service_client.get_container_client(INPUT_CONTAINER_NAME)

# Initialize Azure form recognizer Client
form_recognizer_client = DocumentAnalysisClient(
    endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
)

# Product Categorization Function
def categorize_product(product_name: str):
    """
    Categorize a product name into predefined fields using Azure OpenAI.
    """
    try:
        prompt = f"""
            You are an AI product classifier. Classify the given product name into the following fields in valid JSON format:

            - **Category**: (e.g., 'Food and Beverages', 'Grocery', 'Health and Wellness', 'Home and Kitchen', 'Electronics', 'Kitchen Appliances')
            - **Sub-Category**: (e.g., 'Snacks', 'Vegetables', 'Gadgets')
            - **Cuisine**: (Applicable only for 'Food and Beverages', e.g., Chinese, Italian)
            - **Veg**: (Yes/No, applicable only for 'Food and Beverages')
            - **Description**: (A brief human-readable description)

            ### Product Name: {product_name}

            ### Important Instructions:
            - Return **only** valid JSON.
            - Do **not** include code block markers like ```json or ``` in the response.
            - Do **not** include any explanations, headers, or surrounding text.
            - If the Catogory is not 'Food and Beverages' then in response mention cuisine and veg
              as not applicable. 
            ### JSON Response Template:
            {{
              "Product_Name": "{product_name}",
              "Category": "...",
              "Sub_Category": "...",
              "Cuisine": "...", 
              "Veg": "...",
              "Description": "..."
            }}
        """

        # Call Azure OpenAI
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a product categorization assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.2,
        )

        # Parse the response
        result = response.choices[0].message.content.strip()
        
        # Remove code block markers if present
        if result.startswith("```json"):
            result = result[7:]  # Remove the ```json marker
        if result.endswith("```"):
            result = result[:-3]  # Remove the closing ``` marker

        # Clean up common formatting artifacts
        result = result.strip().replace("\n", "").replace("\\", "")

        try:
            json_result = json.loads(result)
            return json_result
        except json.JSONDecodeError:
            raise ValueError(f"Response is not valid JSON: {result}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Image generation based on the prompt
def generate_image(prompt: str):
    """
    Generate an image using Azure OpenAI DALL-E model.consider only english as lagnguage for text in the image. 
    
    """
    try:
        refined_prompt = (
            f"{prompt}. Please create an image based on the given description, ensuring that a label is visible\
            on the image. The label should read: 'This is a Sample Image, Not Original.'\
            If any text in english language is included in the image, make sure there are no spelling errors. The label should\
            be small yet clearly readable, and properly imprinted on the image."
        )
        
        response = client.images.generate(
            model=AZURE_OPENAI_DEPLOYMENT_NAME_IMG,
            prompt=refined_prompt,
            n=1,
            size="1024x1024"
        )
        
        image_url = response.data[0].url
        return {"status": "success", "image_url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating image: {e}")

#Extract invoce data using form recognizer
async def extract_invoice_data_from_blob(blob_url: str):
    """
    Extract and clean structured data from a PDF file fetched from Blob Storage.
    - **blob_url:** URL of the file stored in Azure Blob Storage.
    """
    temp_pdf_path = None  # Initialize variable to avoid reference error

    try:
        # Download the file from Blob Storage
        blob_client = input_container_client.get_blob_client(blob_url.split("/")[-1])
        blob_stream = blob_client.download_blob()  # No 'await' here
        blob_data = blob_stream.readall()  # Read the blob data synchronously

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(blob_data)
            temp_pdf_path = temp_pdf.name

        # Analyze document using Azure Form Recognizer
        with open(temp_pdf_path, "rb") as pdf_file:
            poller = form_recognizer_client.begin_analyze_document(
                model_id="prebuilt-invoice",
                document=pdf_file
            )
            result = poller.result()

        # Process and clean the result
        # cleaned_data = await analyse_data.process_analysis_result(result, file_name=blob_url.split("/")[-1])
# Process and clean the result
        cleaned_data = await analyse_data.process_analysis_result(
        result, 
        file_name=blob_url.split("/")[-1]
)


        # Save processed data to Blob Output Container
        blob_url_output = await save_to_blob.save_to_blob_storage(cleaned_data, blob_url.split("/")[-1])

        return {
            "status": "success",
            "blob_input_url": blob_url,
            "blob_output_url": blob_url_output,
            "invoice_data": cleaned_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        # Ensure temp file is always cleaned up
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


#Function to get list of file from blob
def fn_get_file_list():
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

        # Access input and output containers
        input_container_client = blob_service_client.get_container_client(INPUT_CONTAINER_NAME)
        output_container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER_NAME)

        # Fetch PDF files with metadata from input container
        pdf_files = [
            {"name": blob.name, "last_modified": blob.last_modified}
            for blob in input_container_client.list_blobs()
            if blob.name.endswith(".pdf")
        ]

        # Fetch JSON files with metadata from output container
        json_files = [
            {"name": blob.name, "last_modified": blob.last_modified}
            for blob in output_container_client.list_blobs()
            if blob.name.endswith(".json")
        ]

        # Match PDF and JSON files
        file_list = []
        for i, pdf_file in enumerate(sorted(pdf_files, key=lambda x: x["last_modified"], reverse=True), start=1):
            # Look for a matching JSON file in the output container
            pdf_base_name = pdf_file["name"].replace(".pdf", "")
            corresponding_json = next(
                (json_file["name"] for json_file in json_files if json_file["name"].replace(".json", "") == pdf_base_name),
                None
            )
            file_list.append({
                "sl_no": i,
                "pdf_file": pdf_file["name"],
                "json_file": corresponding_json,
                "last_modified": pdf_file["last_modified"]
            })

        return {"files": file_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error : {e}")

#Download the file form blob
def fn_download_file(file_name: str):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

    # Determine container based on file type
    if file_name.endswith(".pdf"):
        container_client = blob_service_client.get_container_client(INPUT_CONTAINER_NAME)
    elif file_name.endswith(".json"):
        container_client = blob_service_client.get_container_client(OUTPUT_CONTAINER_NAME)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        # Get the blob client and download the file
        blob_client = container_client.get_blob_client(file_name)
        blob_stream = blob_client.download_blob()

        # Stream the file back to the client
        return StreamingResponse(
            blob_stream.chunks(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")
   