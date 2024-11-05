# backend/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from pydantic import BaseModel
import os
from core.security import create_access_token, get_password_hash, verify_password

prisma = Prisma()
oauth = OAuth()

router = APIRouter()

HF_CLIENT_ID = os.getenv("HF_CLIENT_ID")
HF_CLIENT_SECRET = os.getenv("HF_CLIENT_SECRET")
HF_REDIRECT_URI = os.getenv("HF_REDIRECT_URI")

oauth.register(
    name="huggingface",
    client_id=HF_CLIENT_ID,
    client_secret=HF_CLIENT_SECRET,
    authorize_url="https://huggingface.co/oauth/authorize",
    authorize_params=None,
    access_token_url="https://huggingface.co/oauth/token",
    access_token_params=None,
    client_kwargs={"scope": "openid profile email"},
)

@router.get("/login")
async def login():
    redirect_uri = HF_REDIRECT_URI
    return await oauth.huggingface.authorize_redirect(redirect_uri)

@router.get("/callback")
async def auth_callback(request):
    token = await oauth.huggingface.authorize_access_token(request)
    user_data = await oauth.huggingface.get("https://huggingface.co/api/me", token=token)
    user_info = user_data.json()

    # Upsert user in Prisma
    user = await prisma.user.upsert(
        where={"hf_id": user_info["id"]},
        update={
            "access_token": token["access_token"],
            "refresh_token": token.get("refresh_token"),
            "hashed_password": get_password_hash(user_info["email"])
        },
        create={
            "hf_id": user_info["id"],
            "access_token": token["access_token"],
            "refresh_token": token.get("refresh_token"),
            "hashed_password": get_password_hash(user_info["email"])
        },
    )

    # Generate a JWT for frontend use
    jwt_token = create_jwt_token(user.id)
    response = RedirectResponse(url="/repos")
    response.set_cookie(key="access_token", value=jwt_token, httponly=True)

    return response