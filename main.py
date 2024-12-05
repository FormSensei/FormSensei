from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from db import get_db, init_db
from schemas.post_schema import PostCreate, PostResponse, PostBase
from services.post_service import PostService
from schemas.user_schema import UserCreate, UserResponse
from services.user_service import UserService
from contextlib import asynccontextmanager
from schemas.comment_schema import CommentCreate, CommentResponse
from services.comment_service import CommentService
from fastapi import File, UploadFile
import shutil
import os
from fastapi.staticfiles import StaticFiles

# For Frontend
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import requests
import logging
import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to file
        logging.StreamHandler(),        # Log to console
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application")
    await init_db()
    yield
    logger.info("Shutting down application")
    # You can implement shutdown logic here if needed.
    #await close_db()

app = FastAPI(lifespan=lifespan)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create the directory if it doesn't exist

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# posts

@app.post("/api/v1/post", response_model=PostCreate, status_code=200)
def create_post(post: PostBase, db=Depends(get_db)):
    logger.info(f"POST /posts called with data: {post}")
    post_id = PostService.add_post(db, post)
    logger.info(f"Post successfully added with ID: {post_id}")
    return {"id": post_id, **post.model_dump(), "timestamp": "now"}

@app.get("/api/v1/post/latest", response_model=PostResponse)
def get_post_latest(db=Depends(get_db)):
    """
    Fetch the latest post.
    """
    logger.info("Fetching the latest post")
    post = PostService.get_latest_post(db)
    if not post:
        logger.warning("No posts available.")
        raise HTTPException(status_code=404, detail="No posts available")
    return post

@app.get("/api/v1/post/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db=Depends(get_db)):
    logger.info(f"Fetching post with ID: {post_id}")
    post = PostService.get_post(db, id)
    if not post:
        logger.warning(f"Post with ID {id} not found")
        raise HTTPException(status_code=404, detail="Post not found")
    return post 

@app.get("/api/v1/post/search/{query}", response_model=List[PostResponse])
def search_posts(query: str, db=Depends(get_db)):
    """
    Search for posts based on a query.
    """
    logger.info(f"Searching posts with query: {query}")
    posts = PostService.search_posts(db, query)
    return posts

@app.get("/api/v1/post", response_model=List[PostResponse])
def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db=Depends(get_db)
):
    logger.info(f"Entering /post endpoint with page={page}, limit={limit}")
    try:
        posts = PostService.list_posts(db, page, limit)
        logger.info(f"Posts retrieved: {len(posts)}")
        return posts
    except Exception as e:
        logger.error(f"Error in /posts: {e}")
        raise HTTPException(status_code=500, detail="Error fetching posts")

# users

@app.post("/ai/v1/user", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db=Depends(get_db)):
    logger.info(f"Adding user: {user}")
    try:
        user_id = UserService.add_user(db, user)
        return {"id": user_id, **user.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/user/{user_id}", response_model=UserResponse)
def get_user_by_id(id: int, db=Depends(get_db)):
    logger.info(f"Fetching user with ID: {id}")
    user = UserService.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/v1/user", response_model=List[UserResponse])
def search_users(
    username: Optional[str] = None,
    email: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db=Depends(get_db)
):
    logger.info(f"Searching users, username: {username}, email: {email}, page: {page}, limit: {limit}")
    return UserService.search_users(db, username, email, page, limit)


# comments

@app.post("/api/v1/comment", response_model=CommentResponse, status_code=201)
def create_comment(comment: CommentCreate, db=Depends(get_db)):
    logger.info(f"Adding comment: {comment}")
    comment_id = CommentService.add_comment(db, comment)
    return {"id": comment_id, **comment.dict(), "timestamp": "now"}

@app.get("/api/v1/comment/{post_id}", response_model=List[CommentResponse])
def get_comments(post_id: int, db=Depends(get_db)):
    logger.info(f"Fetching comments for post ID: {post_id}")
    return CommentService.get_comments_by_post(db, post_id)

# images (placeholders)

@app.post("/api/v1/image")
async def post_image():
    raise HTTPException(status_code=501, detail="The image upload functionality is not yet supported.")

@app.get("/api/v1/image/{file_name}")
async def get_image(file_name: str):
    raise HTTPException(status_code=501, detail="The image retrieval functionality is not yet supported.")

# For Frontend
# Initialize templates
templates = Jinja2Templates(directory="templates")

#modified for comments
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    logger.info("Endpoint: GET / (frontend)")
    try:
        # Fetch posts and their comments
        response = requests.get('http://127.0.0.1:8000/api/v1/post')
        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                # Fetch comments for each post
                comments_response = requests.get(f"http://127.0.0.1:8000/api/v1/comment/{post['id']}")
                logger.info(f"Fetched comments: {comments_response.status_code}")
                if comments_response.status_code == 200:
                    post['comments'] = comments_response.json()
                    logger.info(f"Comments: {comments_response.json()}")
                else:
                    post['comments'] = []
        else:
            logger.error(f"Error code fetching posts: {response.status_code}")
            posts = []
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        posts = []
    
    # Render the template with posts and comments
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@app.post("/add-comment")
def add_comment(post_id: int = Form(...), text: str = Form(...), user: str = Form(...)):
    logger.info(f"Adding comment via frontend: post_id={post_id}, user={user}")
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/comment',
            json={"post_id": post_id, "text": text, "user": user}
        )
        if response.status_code == 201:
            logger.info("Comment added successfully via frontend")
    except Exception as e:
        logger.error(f"Error adding comment via frontend: {e}")
    
    return RedirectResponse("/", status_code=303)

@app.get("/submit", response_class=HTMLResponse)
def submit_post_form(request: Request):
    logger.info("Endpoint: GET /submit (frontend)")
    # Render the submit.html form
    return templates.TemplateResponse("submit.html", {"request": request})

@app.post("/submit")
async def submit_post(
    image: UploadFile = File(...),
    text: str = Form(...),
    user: str = Form(...)
):
    try:
        # Save the uploaded image
        image_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # Prepare payload
        payload = {"image": f"/uploads/{image.filename}", "text": text, "user": user}
        logger.info(f"Payload sent to /posts: {payload}")

        # Send the data to /post
        async with httpx.AsyncClient() as client:
            response = await client.post('http://127.0.0.1:8000/api/v1/post', json=payload)
        logger.info(f"Backend /posts response: {response.status_code}, {response.text}")

        if response.status_code != 200:
            logger.error(f"Error from /post: {response.text}")
            raise HTTPException(status_code=500, detail=f"Backend error: {response.text}")

    except Exception as e:
        logger.error(f"Error in /submit: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting post: {e}")

    return RedirectResponse("/", status_code=303)

# End frontend
