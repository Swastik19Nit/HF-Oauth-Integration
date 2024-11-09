from fastapi import APIRouter, Depends, HTTPException, Request
from authlib.integrations.starlette_client import OAuth
from core.security import get_current_active_user
import os
import logging
import requests

router = APIRouter()
oauth = OAuth()

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
    """List all models (repositories) for the specified user from Hugging Face."""
    try:
        access_token = current_user.access_token
        
        if not access_token:
            raise HTTPException(status_code=401, detail="User not authenticated with Hugging Face")
        
        user_response = requests.get(
            "https://huggingface.co/api/whoami-v2",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=user_response.status_code,
                detail="Failed to fetch user information from Hugging Face"
            )
            
        username = user_response.json()["name"]
        
        response = await oauth.huggingface.get(
            f'/api/models?author={username}',
            token={'access_token': access_token}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch models from Hugging Face: {response.text}"
            )
        
        models = response.json()
        return models
        
    except Exception as e:
        logger.error(f"Error fetching models from Hugging Face: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching models from Hugging Face: {str(e)}"
        )

@router.post("/create")
async def create_repository(
    request: Request,
    current_user = Depends(get_current_active_user)
):
    """Create a repository on HuggingFace."""
    try:
        
        body = await request.json()
        name = body.get("name")
        is_private = body.get("private", False)
        
        if not name:
            raise HTTPException(
                status_code=400,
                detail="Repository name is required"
            )

        access_token = current_user.access_token
        
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="User not authenticated with Hugging Face"
            )

        user_response = requests.get(
            "https://huggingface.co/api/whoami-v2",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=user_response.status_code,
                detail="Failed to fetch user information from Hugging Face"
            )
        
        username = user_response.json()["name"]
        
        create_repo_url = "https://huggingface.co/api/repos/create"
        
        repo_data = {
            "type": "model",
            "name": name,
            "organization": username,
            "private": is_private,
            "sdk": "custom"
        }
        
        response = requests.post(
            create_repo_url,
            json=repo_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create repository on Hugging Face: {response.text}"
            )
            
        return response.json()
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating repository on Hugging Face: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating repository: {str(e)}"
        )
    

@router.delete("/delete")
async def delete_repository(
    request: Request,
    current_user = Depends(get_current_active_user)
):
    """Delete a repository from HuggingFace."""
    try:
    
        body = await request.json()
        name = body.get("name")
        organization = body.get("organization")
        
        if not name:
            raise HTTPException(
                status_code=400,
                detail="Repository name is required"
            )

        access_token = current_user.access_token
        
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="User not authenticated with Hugging Face"
            )

        if not organization:
            user_response = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=user_response.status_code,
                    detail="Failed to fetch user information from Hugging Face"
                )
            
            organization = user_response.json()["name"]
        
        delete_repo_url = f"https://huggingface.co/api/repos/delete"
        
        repo_data = {
            "type": "model",
            "name": name,
            "organization": organization
        }
        
        response = requests.delete(
            delete_repo_url,
            json=repo_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code not in [200, 204]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to delete repository on Hugging Face: {response.text}"
            )
            
        return {"message": f"Repository {organization}/{name} successfully deleted"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting repository on Hugging Face: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting repository: {str(e)}"
        )