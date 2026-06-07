from fastapi import FastAPI,HTTPException,File,UploadFile,Form,Depends
from app.schemas import postcreate
from app.db import Post,create_db,get_session
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db()
    yield
    
app=FastAPI(lifespan=lifespan)

@app.post("/posts")
async def create_post(post_data: postcreate, session: AsyncSession = Depends(get_session)):
    post = Post(title=post_data.title, content=post_data.content)
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return {"id": str(post.id), "title": post.title, "content": post.content, "created_on": post.created_on.isoformat()}
    
@app.get("/feed")
async def feed(session: AsyncSession = Depends(get_session)):
    result=await session.execute(select(Post).order_by(Post.created_on.desc()))
    posts=[row[0] for row in result.all()]
    posts_data=[]
    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "title": post.title,
            "content": post.content,
            "created_on": post.created_on.isoformat()
        })
    return {"posts":posts_data}

@app.delete("/posts/{id}")
async def del_post(id:str,session:AsyncSession=Depends(get_session)):
    try:
        post_uuid=uuid.UUID(id)
        res=await session.execute(select(Post).where(Post.id==post_uuid))
        post=res.scalars().first()
        if not post:
            raise HTTPException(status_code=404,detail="Post not found")
        await session.delete(post)
        await session.commit()
        return {"Success":True,"Message":"deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))