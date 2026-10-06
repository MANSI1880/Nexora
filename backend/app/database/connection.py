import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

env_path = os.path.join(os.path.dirname(__file__), "../../.env")
root_env_path = os.path.join(os.path.dirname(__file__), "../../../.env")
load_dotenv(env_path, override=True)
load_dotenv(root_env_path, override=True)

# Use environment variable or default for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/nexora_db")

from sqlalchemy import NullPool
engine = create_async_engine(DATABASE_URL, echo=False, poolclass=NullPool)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
