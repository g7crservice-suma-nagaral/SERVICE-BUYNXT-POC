import os
from dotenv import load_dotenv
from app.model.user_model import UserCredentials
from fastapi import  HTTPException
import uuid
from fastapi import UploadFile
import openai

load_dotenv()

#  ----API key---- 
SESSION_ID = os.getenv("SESSION_ID")

#  ----login---- 

users_db = {
    "admin": {
        "username": "user1",
        "password": "C2LHQ5WjmGpUbkJXrBRd7e"
    }
}

#for both login and logout
logged_in_users = {}

async def fn_login(request: UserCredentials):
    for credentials in users_db.values():
        if credentials['username'] == request.username:
            # Check if the password matches
            if credentials['password'] == request.password:
                return {"success": True, "message": "Login successful", "authid": SESSION_ID}
    raise HTTPException(status_code=400, detail="Invalid login credentials")
   