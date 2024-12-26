# FastAPI Endpoint
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from app.model.category import PromptRequest,ProductResponse
from app.api.endpoints.prod_category import function
from app.core.dependencies import check_api_key 
app=APIRouter(tags=["Az AI Serices"])

@app.post("/generate-image/")
async def generate_image(request: PromptRequest,authorized: bool = Depends(check_api_key)):
    try:
        await asyncio.sleep(20)
        #result = function.generate_image(request.prompt)
        # result={
        #     "status": "success",
        #     "image_url": "https://dalleproduse.blob.core.windows.net/private/images/d7e6ab8c-e948-4afc-a327-6cbb3c5b1075/generated_00.png?se=2024-12-25T11%3A58%3A06Z&sig=TDMBVKQ48H2i34TJgHRMbaN10knOgNJqtwVpzazOcGM%3D&ske=2024-12-27T10%3A41%3A26Z&skoid=09ba021e-c417-441c-b203-c81e5dcd7b7f&sks=b&skt=2024-12-20T10%3A41%3A26Z&sktid=33e01921-4d64-4f8c-a055-5bdaffd5e33d&skv=2020-10-02&sp=r&spr=https&sr=b&sv=2020-10-02"
        # }
        result = function.generate_image(request)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.get("/categorize-product/", response_model=ProductResponse)
async def categorize_product(product_name: str,authorized: bool = Depends(check_api_key)):
    try:
        await asyncio.sleep(10)
        #result = function.categorize_product(product_name)
        result = function.categorize_product(product_name)
        # result=  {
        #     "Product_Name": "Masal Dosa",
        #     "Category": "Food and Beverages",
        #     "Sub_Category": "Snacks",
        #     "Cuisine": "Indian",
        #     "Veg": "Yes",
        #     "Description": "A popular South Indian dish made with a fermented rice and lentil batter, filled with spiced mashed potatoes."
        # }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    
