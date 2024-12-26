from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class ProductResponse(BaseModel):
    Product_Name: str
    Category: str
    Sub_Category: str
    Cuisine: str | None = None  # Optional for non-Food categories
    Veg: str | None = None       # Optional for non-Food categories
    Description: str