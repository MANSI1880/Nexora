from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.tickets import router as tickets_router
from app.api.chat import router as chat_router
from app.auth.jwt import validate_jwt_secret

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_jwt_secret()
    yield

app = FastAPI(title="Nexora API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
