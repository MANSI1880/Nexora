import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def verify():
    url = os.getenv("DATABASE_URL")
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        # Check tables
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';"))
        tables = [row[0] for row in result]
        print(f"Tables in DB: {tables}")
        
        # Check Foreign Keys for tickets
        result = await conn.execute(text("""
            SELECT
                tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY' AND tc.table_schema='public';
        """))
        fks = [(row[0], row[1], row[2], row[3]) for row in result]
        print(f"Foreign Keys: {fks}")
        
        # Check Unique Constraints for users
        result = await conn.execute(text("""
            SELECT
                tc.table_name, kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
            WHERE constraint_type = 'UNIQUE' AND tc.table_schema='public' AND tc.table_name='users';
        """))
        uniques = [(row[0], row[1]) for row in result]
        print(f"Unique constraints on users: {uniques}")
        
        # Or alternatively check indexes for uniqueness
        result = await conn.execute(text("""
            SELECT tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public' AND tablename = 'users' AND indexdef LIKE '%UNIQUE%';
        """))
        unique_indexes = [row[1] for row in result]
        print(f"Unique indexes on users: {unique_indexes}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(verify())
