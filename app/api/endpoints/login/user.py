from fastapi import APIRouter, HTTPException, Depends
from app.model.user_model import UserCredentials
from app.api.endpoints.login import function

user_router=APIRouter(
    tags=["Login"]
)


#  ----login---- 
@user_router.post("/login")
async def fn_login(request: UserCredentials):
    try:
        response = await function.fn_login(request=request)
        return response
    except HTTPException as e:
        return {"success": False, "message": str(e.detail)}
