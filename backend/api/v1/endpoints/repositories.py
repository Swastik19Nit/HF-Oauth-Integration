from fastapi import APIRouter, Depends, HTTPException, Request
from authlib.integrations.starlette_client import OAuth
from core.security import get_current_active_user
import os
import logging

router = APIRouter()
oauth = OAuth()

# Register OAuth client for Hugging Face
oauth.register(
    name='huggingface',
    client_id=os.getenv('HF_CLIENT_ID'),
    client_secret=os.getenv('HF_CLIENT_SECRET'),
    authorize_url='https://huggingface.co/oauth/authorize',
    access_token_url='https://huggingface.co/oauth/token',
    api_base_url='https://huggingface.co/api',
    client_kwargs={'scope': 'profile read-repos write-repos manage-repos'}
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/get")
async def list_repositories(request: Request, current_user = Depends(get_current_active_user)):
    """List all repositories for the current user from Hugging Face."""
    try:
        
        access_token = current_user.access_token
        if not access_token:
            raise HTTPException(status_code=401, detail="User not authenticated with Hugging Face")

       
        response = await oauth.huggingface.get(
            '/repos',  # Hugging Face endpoint for user repositories
            token={'access_token': access_token}
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch repositories from Hugging Face: {response.text}"
            )

        # Parse and return the repositories
        repositories = response.json()
        logger.info(f"Repositories retrieved from Hugging Face: {repositories}")
        return repositories

    except Exception as e:
        logger.error(f"Error fetching repositories from Hugging Face: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching repositories from Hugging Face: {str(e)}"
        )

@router.post("/create")
async def create_repository(
    name: str,
    description: str = None,
    private: bool = False,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a repository in your local database."""
    try:
        if not prisma.is_connected():
            await prisma.connect()

        repository = await prisma.repository.create(
            data={
                "name": name,
                "description": description,
                "private": private,
                "userId": current_user["id"],
            }
        )
        return repository
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create repository: {str(e)}"
        )
