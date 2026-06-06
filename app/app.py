from fastapi import FastAPI,HTTPException
from app.schemas import postcreate
from app.db import post,create_db,get_session
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db()
    yield
app=FastAPI(lifespan=lifespan)

