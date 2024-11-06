from fastapi import APIRouter, Depends, HTTPException, Request
from prisma.models import Repository
from core.security import get_current_active_user
from typing import List
from main import Prisma


router = APIRouter()
prisma = Prisma()


@router.get("/get")  
async def list_repositories(request: Request, current_user: dict = Depends(get_current_active_user)):
    """List all repositories for the current user."""
    try:
        if not prisma.is_connected():
            await prisma.connect()
            
        repositories = await prisma.repository.find_many(
            where={"userId": current_user.id}
        )
        print(f"Found repositories: {repositories}")  
        return repositories
    except Exception as e:
        print(f"Error in list_repositories: {str(e)}") 
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch repositories: {str(e)}"
        )

@router.post("/create")
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