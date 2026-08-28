from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import settings

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    if req.username == settings.admin_username and req.password == settings.admin_password:
        return {"token": "sih-admin-token"}
    raise HTTPException(status_code=401, detail="Invalid username or password")
