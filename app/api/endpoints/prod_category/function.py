from datetime import datetime
from fastapi import  HTTPException
import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
AZURE_OPENAI_DEPLOYMENT_NAME_IMG = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_IMG")


# Initialize Azure OpenAI Client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION
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
        log_error("categorize_product", str(e))
        raise HTTPException(status_code=500, detail=str(e))


def log_error(function_name, error_message):
    """
    Log errors into a file with a timestamp.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Time: {current_time}\nFunction: {function_name}\nError: {error_message}\n"
    os.makedirs("Utils", exist_ok=True)
    with open("Utils/Logs.txt", "a") as file:
        file.write(log_entry)

# ---------------------------------------------------------------------------------------

# def generate_image(prompt: str):
#     """
#     Generate an image using Azure OpenAI DALL-E model.IF any language is being used,
#     Do not make any spelling mistake 
#     If any label is there then keep the label size small   

#     """
#     try:
#         response = client.images.generate(
#             model=AZURE_OPENAI_DEPLOYMENT_NAME_IMG,
#             prompt=prompt,
#             n=1,
#             size="1024x1024"
#         )
#         image_url = response.data[0].url
#         return {"status": "success", "image_url": image_url}

#     except Exception as e:
#         log_error("generate_dalle_image", str(e))
#         raise HTTPException(status_code=500, detail=f"Error generating image: {e}")

def generate_image(prompt: str):
    """
    Generate an image using Azure OpenAI DALL-E model.Do not make any spelling mistake 
    
    """
    try:
        refined_prompt = (
            f"{prompt}. Ensure the image includes a visible label stating: "
            f"IF any language is being used,Do not make any spelling mistake If any label is there then keep the label size small "
            f"clearly readable, and imprinted on the image."
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
        log_error("generate_dalle_image", str(e))
        raise HTTPException(status_code=500, detail=f"Error generating image: {e}")

