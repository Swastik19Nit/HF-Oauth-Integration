# backend/core/security.py
from fastapi_jwt_extended import create_access_token, get_jwt_identity
from datetime import datetime, timedelta
import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")  # Add a default for development
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

def create_jwt_token(user_id: str):
    return create_access_token(
        identity=user_id,
        expires_delta=JWT_ACCESS_TOKEN_EXPIRES
    )