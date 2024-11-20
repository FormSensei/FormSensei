from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from db import get_db, init_db
from schemas.post_schema import PostCreate, PostResponse
from services.post_service import PostService
from schemas.user_schema import UserCreate, UserResponse
from services.user_service import UserService
from contextlib import asynccontextmanager

# For Frontend
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import requests
import logging

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

@app.post("/posts", response_model=PostResponse, status_code=201)
def create_post(post: PostCreate, db=Depends(get_db)):
    logger.info("Endpoint: POST /posts")
    logger.info(f"Adding post: {post}")
    post_id = PostService.add_post(db, post)
    return {"id": post_id, **post.mdoel_dump(), "timestamp": "now"}

@app.get("/posts/{id}", response_model=PostResponse)
def get_post(id: int, db=Depends(get_db)):
    logger.info(f"Fetching post with ID: {id}")
    post = PostService.get_post(db, id)
    if not post:
        logger.warning(f"Post with ID {id} not found")
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/posts", response_model=List[PostResponse])
def list_posts( 
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db=Depends(get_db)
):
    logger.info(f"Listing posts, page: {page}, limit: {limit}")

    return PostService.list_posts(db, page, limit)

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db=Depends(get_db)):
    logger.info(f"Adding user: {user}")
    try:
        user_id = UserService.add_user(db, user)
        return {"id": user_id, **user.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{id}", response_model=UserResponse)
def get_user_by_id(id: int, db=Depends(get_db)):
    logger.info(f"Fetching user with ID: {id}")
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
    logger.info(f"Searching users, username: {username}, email: {email}, page: {page}, limit: {limit}")
    return UserService.search_users(db, username, email, page, limit)

# For Frontend
# Initialize templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    logger.info("Endpoint: GET / (frontend)")
    try:
        # Fetch posts from the backend API
        response = requests.get('http://127.0.0.1:8000/posts')
        if response.status_code == 200:
            posts = response.json()
        else:
            logger.error(f"Error fetching posts: {e}")
            posts = []
    except Exception as e:
        print(f"Error fetching posts: {e}")
        posts = []
    
    # Render the index.html template with the posts data
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

@app.get("/submit", response_class=HTMLResponse)
def submit_post_form(request: Request):
    logger.info("Endpoint: GET /submit (frontend)")
    # Render the submit.html form
    return templates.TemplateResponse("submit.html", {"request": request})

@app.post("/submit")
def submit_post(image: str = Form(...), text: str = Form(...), user: str = Form(...)):
    logger.info("Endpoint: POST /submit (frontend)")
    try:
        # Send post data to the backend API
        response = requests.post(
            'http://127.0.0.1:8000/posts',
            json={"image": image, "text": text, "user": user}
        )
        if response.status_code == 201:
            logger.info("Post submitted successfully via frontend")
            print("Post successfully created!")
    except Exception as e:
        logger.error(f"Error submitting post: {e}")
        print(f"Error submitting post: {e}")
    
    # Redirect to the home page after submitting
    return RedirectResponse("/", status_code=303)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    logger.info("Endpoint: GET /favicon.ico")
    return JSONResponse(content={}, status_code=204)

# End frontend
