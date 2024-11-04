import os
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

class Settings:
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY") 

@AuthJWT.load_config
def get_config():
    return Settings()

def create_jwt_token(user_id: str):
    """Creates a JWT token for the authenticated user."""
    jwt = AuthJWT()
    token = jwt.create_access_token(subject=user_id)
    return token

async def get_current_user(Authorize: AuthJWT = Depends()):
    """Get the current user based on the JWT token."""
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_subject()

    user = await prisma.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
