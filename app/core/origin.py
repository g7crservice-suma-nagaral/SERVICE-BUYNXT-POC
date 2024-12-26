from typing import List
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.api.endpoints.prod_category import category
from app.api.endpoints.login import user

origins=["*"]

def create_middleware()->List[Middleware]:
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True            
        )
    ]
    return middleware

def init_routers(app_:FastAPI)->None:
    app_.include_router(category.app)
    app_.include_router(user.user_router)
