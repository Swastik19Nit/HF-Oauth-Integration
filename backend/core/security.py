# backend/core/security.py
import os
from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from dotenv import load_dotenv

load_dotenv()

@AuthJWT.load_config
def get_jwt_config():
    return AuthJWT(secret_key=os.getenv("JWT_SECRET_KEY"))

def create_jwt_token(user_id: str):
    auth = AuthJWT()
    return auth.create_access_token(subject=user_id)

async def get_current_user(auth: AuthJWT = Depends()):
    try:
        auth.jwt_required()
        user_id = auth.get_jwt_subject()
        user = await prisma.user.find_unique(where={"id": user_id})
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")
