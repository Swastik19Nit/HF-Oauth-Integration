from fastapi import APIRouter, Depends, HTTPException, Request
from prisma.models import Repository
from core.security import get_current_active_user
from typing import List
from main import Prisma


router = APIRouter()
prisma = Prisma()

@router.get("/test")
async def test_route():
    return {"message": "Repository router is working"}

@router.get("")  # Note: using empty string here since prefix will be added in main.py
async def list_repositories(request: Request, current_user: dict = Depends(get_current_active_user)):
    """List all repositories for the current user."""
    try:
        if not prisma.is_connected():
            await prisma.connect()
            
        repositories = await prisma.repository.find_many(
            where={"userId": current_user["id"]}
        )
        print(f"Found repositories: {repositories}")  # Debug log
        return repositories
    except Exception as e:
        print(f"Error in list_repositories: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch repositories: {str(e)}"
        )

@router.post("")
async def create_repository(
    name: str, 
    description: str = None, 
    private: bool = False, 
    current_user: dict = Depends(get_current_active_user)
):
    """Create a repository."""
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