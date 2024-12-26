# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import os
# import json
# from openai import AzureOpenAI
# from dotenv import load_dotenv
# from datetime import datetime

# # Load environment variables
# load_dotenv()

# # Azure OpenAI Configuration
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
# AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
# AZURE_OPENAI_API_VERSION = "2024-02-15-preview"

# # Initialize Azure OpenAI Client
# client = AzureOpenAI(
#     api_key=AZURE_OPENAI_KEY,
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
#     api_version=AZURE_OPENAI_API_VERSION
# )

# # Initialize FastAPI app
# app = FastAPI(title="Categorizing The Products Based On Product Name")

# class ProductRequest(BaseModel):
#     product_name: str

# class ProductResponse(BaseModel):
#     Product_Name: str
#     Category: str
#     Sub_Category: str
#     Cuisine: str | None = None  # Optional for non-Food categories
#     Veg: str | None = None       # Optional for non-Food categories
#     Description: str

# # Product Categorization Function
# def categorize_product(product_name: str):
#     """
#     Categorize a product name into predefined fields using Azure OpenAI.
#     """
#     try:
#         prompt = f"""
#             You are an AI product classifier. Classify the given product name into the following fields in valid JSON format:

#             - **Category**: (e.g., 'Food and Beverages', 'Grocery', 'Health and Wellness', 'Home and Kitchen', 'Electronics', 'Kitchen Appliances')
#             - **Sub-Category**: (e.g., 'Snacks', 'Vegetables', 'Gadgets')
#             - **Cuisine**: (Applicable only for 'Food and Beverages', e.g., Chinese, Italian)
#             - **Veg**: (Yes/No, applicable only for 'Food and Beverages')
#             - **Description**: (A brief human-readable description)

#             ### Product Name: {product_name}

#             ### Important Instructions:
#             - Return **only** valid JSON.
#             - Do **not** include code block markers like ```json or ``` in the response.
#             - Do **not** include any explanations, headers, or surrounding text.

#             ### JSON Response Template:
#             {{
#               "Product_Name": "{product_name}",
#               "Category": "...",
#               "Sub_Category": "...",
#               "Cuisine": "...",
#               "Veg": "...",
#               "Description": "..."
#             }}
#         """

#         # Call Azure OpenAI
#         response = client.chat.completions.create(
#             model=AZURE_OPENAI_DEPLOYMENT_NAME,
#             messages=[
#                 {"role": "system", "content": "You are a product categorization assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=200,
#             temperature=0.2,
#         )

#         # Parse the response
#         result = response.choices[0].message.content.strip()
        
#         # Remove code block markers if present
#         if result.startswith("```json"):
#             result = result[7:]  # Remove the ```json marker
#         if result.endswith("```"):
#             result = result[:-3]  # Remove the closing ``` marker

#         # Clean up common formatting artifacts
#         result = result.strip().replace("\n", "").replace("\\", "")

#         try:
#             json_result = json.loads(result)
#             return json_result
#         except json.JSONDecodeError:
#             raise ValueError(f"Response is not valid JSON: {result}")

#     except Exception as e:
#         log_error("categorize_product", str(e))
#         raise HTTPException(status_code=500, detail=str(e))

# # Error Logging
# def log_error(function_name, error_message):
#     """
#     Log errors into a file with a timestamp.
#     """
#     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     log_entry = f"Time: {current_time}\nFunction: {function_name}\nError: {error_message}\n"
#     os.makedirs("Utils", exist_ok=True)
#     with open("Utils/Logs.txt", "a") as file:
#         file.write(log_entry)

# # FastAPI Endpoint
# @app.post("/categorize-product/", response_model=ProductResponse)
# async def categorize_product_endpoint(request: ProductRequest):
#     """
#     Endpoint to categorize a product using Azure OpenAI.
#     """
#     try:
#         result = categorize_product(request.product_name)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI
import logging,os

from app.core.origin import create_middleware, init_routers

def create_app()->FastAPI:
    app_=FastAPI(middleware=create_middleware(),title="Azure AI services",
                 version="V1.0")
    # filepath=os.path.join("utils","Basic.logs")
    # logging.basicConfig(level=logging.DEBUG,
    #                     filename=filepath,
    #                     format="%(asctime)s || %(levelname)s || %(message)s",
    #                     datefmt="%Y-%m-%d %H:%M:%S")
    init_routers(app_=app_)
    return app_

app= create_app()


