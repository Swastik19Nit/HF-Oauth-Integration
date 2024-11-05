# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma
from contextlib import asynccontextmanager
from fastapi_jwt_extended import JWTManager
from api.v1.endpoints import repositories
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    prisma = Prisma()
    await prisma.connect()
    yield
    await prisma.disconnect()

app = FastAPI(lifespan=lifespan)


# Setup JWT
app.config = {
    "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
}
jwt = JWTManager(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repositories.router, prefix="/api/v1/repositories")
print("Starting FastAPI application...")
