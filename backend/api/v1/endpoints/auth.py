# backend/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from httpx import AsyncClient
import os
from core.security import create_jwt_token

router = APIRouter()
prisma = Prisma()

HF_CLIENT_ID = os.getenv("HF_CLIENT_ID")
HF_CLIENT_SECRET = os.getenv("HF_CLIENT_SECRET")
HF_REDIRECT_URI = os.getenv("HF_REDIRECT_URI")

@router.get("/login")
async def login():
    hf_authorize_url = (
        f"https://huggingface.co/oauth/authorize?"
        f"client_id={HF_CLIENT_ID}&response_type=code&redirect_uri={HF_REDIRECT_URI}"
    )
    return {"login_url": hf_authorize_url}

@router.get("/callback")
async def callback(code: str):
    async with AsyncClient() as client:
        response = await client.post(
            "https://huggingface.co/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": HF_CLIENT_ID,
                "client_secret": HF_CLIENT_SECRET,
                "redirect_uri": HF_REDIRECT_URI,
                "code": code,
            },
        )
        token_data = response.json()
    
    hf_id = token_data["user"]["id"]
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    user = await prisma.user.upsert(
        where={"hf_id": hf_id},
        update={"access_token": access_token, "refresh_token": refresh_token},
        create={
            "hf_id": hf_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
    )

    jwt_token = create_jwt_token(user.id)
    return {"token": jwt_token}
