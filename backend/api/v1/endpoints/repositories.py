# backend/api/v1/endpoints/repositories.py
from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from core.security import get_current_user

router = APIRouter()
prisma = Prisma()

@router.post("/")
async def create_repository(name: str, description: str = None, private: bool = False, current_user=Depends(get_current_user)):
    repository = await prisma.repository.create(
        data={
            "name": name,
            "description": description,
            "private": private,
            "userId": current_user.id,
        }
    )
    return repository

@router.get("/")
async def list_repositories(current_user=Depends(get_current_user)):
    repositories = await prisma.repository.find_many(where={"userId": current_user.id})
    return repositories

@router.delete("/{repo_id}")
async def delete_repository(repo_id: str, current_user=Depends(get_current_user)):
    await prisma.repository.delete(
        where={"id": repo_id, "userId": current_user.id}
    )
    return {"message": "Repository deleted successfully"}
