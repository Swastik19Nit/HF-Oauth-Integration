import os
from fastapi import APIRouter, Depends, HTTPException
from prisma.models import Repository
from app.core.security import AuthJWT
import requests

router = APIRouter()
BASE_HF_URL = "https://api.huggingface.co"

@router.post("/repositories")
async def create_repository(
    name: str,
    description: str = None,
    private: bool = False,
    Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()

  
    access_token = Authorize.get_jwt_subject()  
    response = requests.post(
        f"{BASE_HF_URL}/api/repos/create",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": name, "private": private},
    )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to create repository on Hugging Face")

    repository = await prisma.repository.create(
        data={
            "name": name,
            "description": description,
            "private": private,
            "userId": user_id,
        }
    )
    return repository

@router.get("/repositories")
async def list_repositories(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()

    repositories = await prisma.repository.find_many(where={"userId": user_id})
    return repositories

@router.delete("/repositories/{repo_id}")
async def delete_repository(repo_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()
    await prisma.repository.delete(where={"id": repo_id, "userId": user_id})
    return {"message": "Repository deleted successfully"}
