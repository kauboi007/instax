from collections.abc import AsyncGenerator
import uuid
from sqlalchemy import Column,String,Text,DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import  UUID
from sqlalchemy.ext.asyncio import async_sessionmaker,AsyncSession,create_async_engine
from sqlalchemy.orm import DeclarativeBase,relationship
from datetime import datetime,timezone,timedelta

DATABASE_URL="sqlite+aiosqlite:///./test.db"
class base(DeclarativeBase):
    pass

class Post(base):   
    __tablename__="posts"
    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    content=Column(Text)
    title=Column(Text)
    created_on=Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=5, minutes=30))))

engine=create_async_engine(DATABASE_URL)
async_session_maker=async_sessionmaker(engine,expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

async def get_session():
    async with async_session_maker() as session:
        yield session