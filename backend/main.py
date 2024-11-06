from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma
from contextlib import asynccontextmanager
from api.v1.endpoints import repositories
from starlette.middleware.sessions import SessionMiddleware
from api.v1.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    prisma = Prisma()
    await prisma.connect()
    yield
    await prisma.disconnect()

app = FastAPI(lifespan=lifespan)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secure-secret-key"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(repositories.router, prefix="/api/v1/repositories", tags=["repositories"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

print("Starting FastAPI application...")
