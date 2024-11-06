from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from prisma import Prisma
import os
from core.security import create_access_token, get_password_hash

prisma = Prisma()
config = Config('.env')
oauth = OAuth(config)

router = APIRouter()

oauth.register(
    name='huggingface',
    client_id=os.getenv('HF_CLIENT_ID'),
    client_secret=os.getenv('HF_CLIENT_SECRET'),
    authorize_url='https://huggingface.co/oauth/authorize',
    access_token_url='https://huggingface.co/oauth/token',
    api_base_url='https://huggingface.co/api',
    client_kwargs={'scope': 'profile read-repos write-repos manage-repos'}
)

@router.get("/login")
async def login_via_huggingface(request: Request):
    """
    Initiate the HuggingFace OAuth login process
    """
    # Use request.url_for to generate the callback URL dynamically
    # Make sure you have registered this route name in your FastAPI app
    redirect_uri = request.url_for('auth_via_huggingface')
    return await oauth.huggingface.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_via_huggingface(request: Request):
    """
    Handle the HuggingFace OAuth callback
    """
    try:
        token = await oauth.huggingface.authorize_access_token(request)
        print("Token:", token)

        resp = await oauth.huggingface.get('https://huggingface.co/api/me', token=token)
        print("Response:", resp)
        user_info = resp.json()
        print("User Info:", user_info)

        
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

        # Generate JWT
        jwt_token = create_access_token(user.id)
        response = RedirectResponse(url="/repos")
        response.set_cookie(key="access_token", value=jwt_token, httponly=True)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Authentication failed: {str(e)}"
        )