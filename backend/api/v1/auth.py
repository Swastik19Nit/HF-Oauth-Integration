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
from pprint import pformat
import logging
import requests
from datetime import datetime, timedelta
from core.security import create_access_token, get_password_hash

prisma = Prisma()
config = Config('.env')
oauth = OAuth(config)

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth.register(
    name='huggingface',
    client_id=os.getenv('HF_CLIENT_ID'),
    client_secret=os.getenv('HF_CLIENT_SECRET'),
    authorize_url='https://huggingface.co/oauth/authorize',
    access_token_url='https://huggingface.co/oauth/token',
    api_base_url='https://huggingface.co/api',
    client_kwargs={'scope': 'profile read-repos write-repos manage-repos'}
)

async def log_request_details(request: Request):
    """
    Comprehensive logging of request object details, especially useful for OAuth callbacks
    """
    try:
        request_info = {
            "base_info": {
                "method": request.method,
                "url": str(request.url),
                "base_url": str(request.base_url),
                "path": request.url.path,
            },
            "query_params": dict(request.query_params),
            "path_params": dict(request.path_params),
            "headers": dict(request.headers),
            "cookies": dict(request.cookies),
            "client": {
                "host": request.client.host if request.client else None,
                "port": request.client.port if request.client else None
            }
        }

       
        state = request.query_params.get('state')
        code = request.query_params.get('code')
        if state or code:
            request_info["oauth_specific"] = {
                "state": state,
                "code": code
            }

        # Try to get body content if any
        try:
            body = await request.body()
            if body:
                request_info["body"] = body.decode()
                try:
                    request_info["body_json"] = await request.json()
                except:
                    pass
        except:
            request_info["body"] = "Could not read body"

        # Log the formatted information
        logger.info("=== OAuth Callback Request Details ===")
        logger.info(f"Full request info:\n{pformat(request_info)}")
        
        return request_info

    except Exception as e:
        logger.error(f"Error logging request details: {str(e)}")
        raise

@router.get("/login")
async def login_via_huggingface(request: Request):
    await log_request_details(request)
    """Initiate the Hugging Face OAuth login process."""
    redirect_uri = request.url_for('auth_via_huggingface')
    return await oauth.huggingface.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_via_huggingface(request: Request):

    try:
        if not prisma.is_connected():
            await prisma.connect()
            print("Connected to Hugging Face")

        await log_request_details(request)
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
          
        
        response = requests.get(
            "https://huggingface.co/api/whoami-v2",
            params={},
            headers={"Authorization":f"Bearer {token['access_token']}"}
        )
        print(response.json()["name"])  #username:Swastik19


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
                    "refresh_token": token.get("refresh_token"), #algorithm 
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
            key="actwt",
            value=jwt_token,
            httponly=True,
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
