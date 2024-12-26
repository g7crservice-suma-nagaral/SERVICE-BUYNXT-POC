from fastapi.security import APIKeyHeader
from fastapi import Depends,HTTPException

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("SESSION_ID")

# Define the dependency for API Key
api_key_header = APIKeyHeader(name="API-Key")

# Dependency function to check the API key
def check_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return True
    else:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized", "data": ""})