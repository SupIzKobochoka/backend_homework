from fastapi import APIRouter, Depends, HTTPException, Response
from db_scripts.auth import AuthService
from schemas.account import LoginRequest

router = APIRouter()


@router.post("/login")
async def login(data: LoginRequest, response: Response, auth_service: AuthService = Depends()):
    token = await auth_service.login(data.login, data.password)
    if token is None:
        raise HTTPException(401, detail="Invalid credentials")

    response.set_cookie("access_token", token, httponly=True, samesite="lax")
    return {"status": "ok"}
