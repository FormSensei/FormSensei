from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from db import get_db, init_db
from schemas.post_schema import PostCreate, PostResponse
from services.post_service import PostService
from schemas.user_schema import UserCreate, UserResponse
from services.user_service import UserService
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await init_db()
    yield  # This is where the application runs
    # Shutdown logic
    #await close_db()

app = FastAPI(lifespan=lifespan)

@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db=Depends(get_db)):
    post_id = PostService.add_post(db, post)
    return {"id": post_id, **post.mdoel_dump(), "timestamp": "now"}

@app.get("/posts/{id}", response_model=PostResponse)
def get_post(id: int, db=Depends(get_db)):
    post = PostService.get_post(db, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/posts", response_model=List[PostResponse])
def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db=Depends(get_db)
):
    return PostService.list_posts(db, page, limit)

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db=Depends(get_db)):
    try:
        user_id = UserService.add_user(db, user)
        return {"id": user_id, **user.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{id}", response_model=UserResponse)
def get_user_by_id(id: int, db=Depends(get_db)):
    user = UserService.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=List[UserResponse])
def search_users(
    username: Optional[str] = None,
    email: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db=Depends(get_db)
):
    return UserService.search_users(db, username, email, page, limit)