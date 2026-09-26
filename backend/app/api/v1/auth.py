from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import redis.asyncio as aioredis
from app.config import settings
from app.api.deps import get_redis

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/login")
async def login(req: LoginRequest, redis: aioredis.Redis = Depends(get_redis)):
    if req.username != settings.admin_username:
        raise HTTPException(status_code=401, detail="Invalid username")
        
    override = await redis.get("admin_password_override")
    active_password = override if override else settings.admin_password
    
    if req.password == active_password:
        return {"token": "admin-token"}
    raise HTTPException(status_code=401, detail="Invalid password")

@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, redis: aioredis.Redis = Depends(get_redis)):
    override = await redis.get("admin_password_override")
    active_password = override if override else settings.admin_password
    
    if req.current_password != active_password:
        raise HTTPException(status_code=403, detail="Current password is incorrect")
        
    await redis.set("admin_password_override", req.new_password)
    return {"status": "success", "message": "Password updated successfully"}

@router.post("/forgot-password")
async def forgot_password(redis: aioredis.Redis = Depends(get_redis)):
    """Mock forgot password for demo purposes."""
    await redis.delete("admin_password_override")
    return {"status": "success", "message": "Demo Mode: Password has been reset to default 'admin123'."}
