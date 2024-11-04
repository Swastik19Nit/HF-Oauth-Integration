# backend/api/v1/endpoints/auth.py

from fastapi import APIRouter, HTTPException, Depends
from prisma import Prisma
import os
import requests
from app.core.security import create_jwt_token

router = APIRouter()
prisma = Prisma()

HF_API_URL = "https://api.huggingface.co"
SECRET_KEY = os.getenv("JWT_SECRET_KEY") 
@router.post("/login")
async def login(hf_access_token: str):
   
    headers = {"Authorization": f"Bearer {hf_access_token}"}
    response = requests.get(f"{HF_API_URL}/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Hugging Face access token")

   
    user_data = response.json()
    hf_id = user_data.get("id")

    
    user = await prisma.user.upsert(
        where={"hf_id": hf_id},
        update={"access_token": hf_access_token},
        create={"hf_id": hf_id, "access_token": hf_access_token},
    )

    
    jwt_token = create_jwt_token(user.id)
    return {"token": jwt_token}
