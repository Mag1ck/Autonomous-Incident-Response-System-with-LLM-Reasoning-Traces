from datetime import datetime
from typing import Literal
import os
from databases import User
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")

app = FastAPI()

engine = create_async_engine(f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@postgres/{PG_DB}")
async_session = async_sessionmaker(engine, expire_on_commit=False)

class UserResponse(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    user_id: str
    status: Literal["active", "blocked"]
    created_at: datetime
    updated_at: datetime

class UserEligibilityResponse(BaseModel):
    user_id: str
    eligible: bool
    reason: str | None

@app.get("/health")
def get_health():
    return {"status": "healthy"}   

@app.get("/users/{user_id}/eligibility", response_model = UserEligibilityResponse)
async def check_user_eligibility(user_id: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code = 404, detail = "User not found")
    eligible = user.status == "active"
    return {"user_id": user.user_id, "eligible": eligible,
            "reason": None if eligible else f"user_{user.status}"}