import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.tickets import router as tickets_router
from app.api.chat import router as chat_router
from app.auth.jwt import validate_jwt_secret
from app.database.connection import AsyncSessionLocal

DEFAULT_CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

def get_cors_origins(cors_env: str | None = None) -> list[str]:
    raw = cors_env if cors_env is not None else os.getenv("CORS_ORIGINS")
    if not raw:
        return DEFAULT_CORS_ORIGINS.copy()
    origins = [origin.strip() for origin in raw.split(",") if origin.strip() and origin.strip() != "*"]
    return origins if origins else DEFAULT_CORS_ORIGINS.copy()

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_jwt_secret()
    yield

app = FastAPI(title="Nexora API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(chat_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Nexora API"}

@app.get("/health")
async def health_check():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected"}
        )
