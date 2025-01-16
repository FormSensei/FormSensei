from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from db import get_db, init_db
from schemas.post_schema import PostCreate, PostResponse, PostBase
from services.post_service import PostService
from schemas.user_schema import UserCreate, UserResponse
from services.user_service import UserService
from contextlib import asynccontextmanager
from schemas.comment_schema import CommentCreate, CommentResponse
from services.comment_service import CommentService
from schemas.authentication_schema import Authentication, AuthenticationResponse
from services.authentication_service import AuthenticationService
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
import shutil
import os

import logging

#For message service
import pika
from fastapi.responses import FileResponse

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

UPLOAD_DIR = "uploads/full"
REDUCED_DIR = "uploads/reduced"
#os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create the directory if it doesn't exist

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
    limit: int = Query(50, ge=1),
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

@app.post("/api/v1/user", response_model=UserResponse, status_code=201)
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
    try:
        result = CommentService.add_comment(db, comment)  # Now returns a dict with id and time_created
        response = {
            "id": result["id"],
            "post_id": comment.post_id,
            "text": comment.text,
            "username": comment.username,
            "time_created": result["time_created"],  # Include time_created from DB
        }
        logger.info(f"Comment response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(status_code=500, detail="Error adding comment.")


@app.get("/api/v1/comment/{post_id}", response_model=List[CommentResponse])
def get_comments(post_id: int, db=Depends(get_db)):
    logger.info(f"Fetching comments for post ID: {post_id}")
    try:
        comments = CommentService.get_comments_by_post(db, post_id)
        if not comments:
            logger.warning(f"No comments found for post ID: {post_id}")
        else:
            logger.info(f"Comments fetched for post ID {post_id}: {comments}")
        return comments
    except Exception as e:
        logger.error(f"Error fetching comments for post ID {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching comments.")

# For message service

# RabbitMQ setup
QUEUE_NAME = "image_resize"

def send_message_to_rabbitmq(file_path: str):
    """Send a message to RabbitMQ to trigger image resizing."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)
        channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=file_path)
        logger.info(f"Message sent to RabbitMQ for resizing: {file_path}")
        connection.close()
    except Exception as e:
        logger.error(f"Failed to send message to RabbitMQ: {e}")
        #raise HTTPException(status_code=500, detail="Failed to enqueue image resize task.")


# images (placeholders)
@app.post("/api/v1/image")
async def upload_image(image: UploadFile = File(...)):
    """Upload an image and enqueue it for resizing."""
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    try:
        # Save the uploaded image
        with open(file_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        logger.info(f"Image saved: {file_path}")

        # Send message to RabbitMQ
        send_message_to_rabbitmq(image.filename)

        return {"message": "Image uploaded and resize task enqueued.", "image_path": image.filename}
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Error uploading image.")

@app.get("/api/v1/image/reduced/{file_name}")
async def get_reduced_image(file_name: str):
    """Serve the reduced-size image."""
    reduced_path = os.path.join(REDUCED_DIR, file_name)
    if not os.path.exists(reduced_path):
        raise HTTPException(status_code=404, detail="Reduced-size image not found.")
    return FileResponse(reduced_path)

@app.get("/api/v1/image/full/{file_name}")
async def get_full_image(file_name: str):
    """Serve the full-size image."""
    logger.info(f"Trying to get image: {file_name}")
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Full-size image not found.")
    return FileResponse(file_path)


# authentication

@app.post("/api/v1/authenticate", response_model=AuthenticationResponse, status_code=201)
async def authenticate(authentication: Authentication, db=Depends(get_db)):
    logger.info(f"Trying to authenticate user: {authentication.username}")
    try:
        result = AuthenticationService.authenticate_user(db, authentication)  # Now returns a dict with id and time_created
        response = {
            "valid": result
        }
        logger.info(f"Authentication response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error authenticating: {e}")
        raise HTTPException(status_code=500, detail="Error authenticating.")
    
