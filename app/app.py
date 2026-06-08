from fastapi import FastAPI,HTTPException,Depends
from app.schemas import postcreate
from app.db import Post,create_db,get_session,user
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid
from sqlalchemy.orm import selectinload
from app.schemas import user_create,user_read,user_update
from app.users import  auth_backend,current_active_user,fastapi_users
@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db()
    yield
    
app=FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend),prefix="/auth/jwt",tags=['auth'])
app.include_router(fastapi_users.get_register_router(user_read,user_create),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_verify_router(user_read),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_users_router(user_read,user_update),prefix="/users",tags=["users"])

@app.post("/posts")
async def create_post(post_data: postcreate, session: AsyncSession = Depends(get_session),user:user=Depends(current_active_user)):
    post = Post(title=post_data.title, content=post_data.content,user_id=user.id)
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return {"id": str(post.id), "title": post.title, "content": post.content, "created_on": post.created_on.isoformat()}
    
@app.get("/feed")
async def feed(session: AsyncSession = Depends(get_session),user:user=Depends(current_active_user)):
    result=await session.execute(select(Post).order_by(Post.created_on.desc()))
    posts=[row[0] for row in result.all()]
    posts_data=[]
    result = await session.execute(
        select(Post)
        .options(selectinload(Post.user))
        .order_by(Post.created_on.desc())
    )   
    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "user_id":str(post.user_id),
            "title": post.title,
            "content": post.content,
            "created_on": post.created_on.isoformat(),
            "is_owner":post.user_id==user.id,
            "email":post.user.email
        })
    return {"posts":posts_data}

@app.delete("/posts/{id}")
async def del_post(id: str, session: AsyncSession = Depends(get_session), current_user: user = Depends(current_active_user)):
    try:
        post_uuid = uuid.UUID(id)
        res = await session.execute(select(Post).where(Post.id == post_uuid))
        post = res.scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="you cant delete the post")
        await session.delete(post)
        await session.commit()
        return {"Success": True, "Message": "deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))