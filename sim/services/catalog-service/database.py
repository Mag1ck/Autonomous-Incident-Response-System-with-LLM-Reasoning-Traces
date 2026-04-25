import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

PG_USER = os.getenv('PG_USER')
PG_PASS = os.getenv('PG_PASS')
PG_DB = os.getenv('PG_DB')

async def async_main():
#Main program function.

    engine = create_async_engine(
        f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@postgres/{PG_DB}"
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)

