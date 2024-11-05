from fastapi import APIRouter, Depends, HTTPException
from prisma.models import Repository
from fastapi_jwt_extended import jwt_required, get_jwt_identity
from typing import List

router = APIRouter()

@router.post("/")
@jwt_required()
async def create_repository(name: str, description: str = None, private: bool = False):
    user_id = get_jwt_identity()
    
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
@jwt_required()
async def list_repositories():
    user_id = get_jwt_identity()
    repositories = await prisma.repository.find_many(where={"userId": user_id})
    return repositories