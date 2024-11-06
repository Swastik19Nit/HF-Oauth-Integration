from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma
from contextlib import asynccontextmanager
from api.v1.endpoints import repositories
from starlette.middleware.sessions import SessionMiddleware
from api.v1.auth import router as auth_router
import os

prisma = Prisma()

@asynccontextmanager
async def lifespan(app: FastAPI):
   
    await prisma.connect()
    yield
    
    await prisma.disconnect()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from api.v1.endpoints.repositories import router as repository_router
app.include_router(
    repository_router,
    prefix="/api/v1/repositories",
    tags=["repositories"]
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "API is working"}

print("Starting FastAPI application...")
