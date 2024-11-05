from fastapi import APIRouter, Depends, HTTPException
from prisma.models import Repository
from core.security import get_current_active_user, get_jwt_identity
from typing import List

router = APIRouter()

@router.post("/")
async def create_repository(name: str, description: str = None, private: bool = False, current_user: dict = Depends(get_current_active_user)):
    user_id = current_user["id"]
    repository = await prisma.repository.create({
        "data": {
            "name": name,
            "description": description,
            "private": private,
            "userId": user_id,
        }
    })
    return repository

@router.get("/", response_model=List[Repository])
async def list_repositories(current_user: dict = Depends(get_current_active_user)):
    user_id = current_user["id"]
    repositories = await prisma.repository.find_many(where={"userId": user_id})
    return repositories