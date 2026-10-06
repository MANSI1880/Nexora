import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    # Test the fallback URL to see if it is available
    url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/nexora_db")
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            print("Connected successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
