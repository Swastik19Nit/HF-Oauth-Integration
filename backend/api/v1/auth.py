from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth # type: ignore
from prisma import Prisma
import os
import base64
import json
from main import Prisma
from datetime import datetime, timedelta
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
    """Initiate the Hugging Face OAuth login process."""
    redirect_uri = request.url_for('auth_via_huggingface')
    return await oauth.huggingface.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_via_huggingface(request: Request):

    try:
        if not prisma.is_connected():
            await prisma.connect()
            print("Connected to Hugging Face")

        
        token = await oauth.huggingface.authorize_access_token(request)
        
        

        token_parts = token['access_token'].split('.')
        if len(token_parts) != 3:
            raise HTTPException(
                status_code=400,
                detail="Invalid access token format"
            )

        def add_padding(b64str):
            padding = 4 - (len(b64str) % 4)
            return b64str + ("=" * padding)

        payload = token_parts[1]
        payload = add_padding(payload.replace('-', '+').replace('_', '/'))

        decoded_payload = json.loads(base64.b64decode(payload))

        hf_user_id = str(decoded_payload.get('sub'))
        if not hf_user_id:
            raise HTTPException(
                status_code=400,
                detail="User ID not found in token payload"
            )

        print(f"Decoded user ID: {hf_user_id}")

        existing_user = await prisma.user.find_unique(
            where={"hf_id": hf_user_id}
        )

        if existing_user:
           
            user = await prisma.user.update(
                where={"id": existing_user.id},
                data={
                    "access_token": token["access_token"],
                    "refresh_token": token.get("refresh_token"),
                    "last_login": datetime.utcnow()
                }
            )
        else:
           
            user = await prisma.user.create(
                data={
                    "hf_id": hf_user_id,
                    "access_token": token["access_token"],
                    "refresh_token": token.get("refresh_token"),
                    "hashed_password": get_password_hash(hf_user_id),
                    "created_at": datetime.utcnow(),
                    "last_login": datetime.utcnow()
                }
            )

       
        jwt_token = create_access_token(
            user.id,
            expires_delta=timedelta(days=7)  # Longer session token
        )

       
        response = RedirectResponse(url="http://localhost:3000/repositories")
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=True,
            samesite='lax',
            max_age=7 * 24 * 3600 
        )

        response.set_cookie(
            key="logged_in",
            value="true",
            httponly=False,
            secure=True,
            samesite='lax',
            max_age=7 * 24 * 3600
        )

        return response

    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=400,
            detail=f"Authentication failed: {str(e)}"
        )
