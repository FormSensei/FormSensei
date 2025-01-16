from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
import requests
import logging
import httpx
import os
import shutil

logging.basicConfig(
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to file
        logging.StreamHandler(),        # Log to console
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()


UPLOAD_DIR = "uploads"
#os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create the directory if it doesn't exist

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(SessionMiddleware, secret_key="test123", max_age=None)

# Initialize templates
templates = Jinja2Templates(directory="templates")

#modified for comments
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    logger.info("Endpoint: GET / (frontend)")
    try:
        # Fetch posts and their comments
        response = requests.get('http://fastapi-app:8080/api/v1/post')
        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                # Fetch comments for each post
                comments_response = requests.get(f"http://fastapi-app:8080/api/v1/comment/{post['id']}")
                logger.info(f"Fetched comments: {comments_response.status_code}")
                if comments_response.status_code == 200:
                    post['comments'] = comments_response.json()
                    logger.info(f"Comments: {comments_response.json()}")
                else:
                    post['comments'] = []

                # Construct image URL if image is present
                image_path = post.get("image")
                if image_path:
                    logger.info(f"Image: {image_path}")
                    post['image_url'] = f"http://localhost:8080/api/v1/image/reduced/{os.path.basename(image_path)}"
                    post['full_image_url'] = f"http://localhost:8080/api/v1/image/full/{os.path.basename(image_path)}"
                else:
                    post['image_url'] = None
                    post['full_image_url'] = None
                
        else:
            logger.error(f"Error code fetching posts: {response.status_code}")
            posts = []
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        posts = []
    
    # Render the template with posts and comments
    is_logged_in = False
    if request.session.get("username"):
        is_logged_in = True
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts, "is_logged_in": is_logged_in})


@app.post("/add-comment")
def add_comment(request: Request, post_id: int = Form(...), text: str = Form(...)):
    user = request.session.get("username")
    if not user:
        logger.error("User is not logged in. Cannot add comment.")
        raise HTTPException(status_code=401, detail="User is not logged in")

    logger.info(f"Adding comment via frontend: post_id={post_id}, user={user}")
    try:
        response = requests.post(
            'http://fastapi-app:8080/api/v1/comment',
            json={"post_id": post_id, "text": text, "username": user}
        )
        if response.status_code == 201:
            logger.info("Comment added successfully via frontend")
        else:
            logger.error(f"Error adding comment: {response.text}")
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
    request: Request,
    image: UploadFile = File(...),
    text: str = Form(...)
):
    username = request.session.get("username")
    if not username:
        logger.error("User is not logged in")
        raise HTTPException(status_code=401, detail="User is not logged in")

    try:

        # Upload the image directly to the image API
        files = {
            "image": (image.filename, image.file, image.content_type),
        }

        async with httpx.AsyncClient() as client:
            image_response = await client.post(
                'http://fastapi-app:8080/api/v1/image',
                files=files,
            )

        # Log the image upload response
        logger.info(f"Image upload response: {image_response.status_code}, {image_response.text}")

        if image_response.status_code != 200:
            logger.error(f"Error uploading image: {image_response.text}")
            raise HTTPException(status_code=500, detail=f"Error uploading image: {image_response.text}")

        # Extract the image path from the response
        image_data = image_response.json()
        image_path = image_data.get("image_path")
        if not image_path:
            logger.error("Image path not returned from the API")
            raise HTTPException(status_code=500, detail="Image path not returned from the API")

        # Prepare the post payload with the uploaded image path
        post_payload = {
            "text": text,
            "username": username,
            "image": image_path,
        }

        # Submit the post data to the post API
        async with httpx.AsyncClient() as client:
            post_response = await client.post(
                'http://fastapi-app:8080/api/v1/post',
                json=post_payload,
            )

        logger.info(f"Post submission response: {post_response.status_code}, {post_response.text}")

        if post_response.status_code != 200:
            logger.error(f"Error submitting post: {post_response.text}")
            raise HTTPException(status_code=500, detail=f"Error submitting post: {post_response.text}")


    except Exception as e:
        logger.error(f"Error in /submit: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting post: {e}")

    return RedirectResponse("/", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    logger.info("Endpoint: GET /login (frontend)")
    # Render the submit.html form
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    logger.info("Endpoint: POST /login (frontend)")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'http://fastapi-app:8080/api/v1/authenticate',
                json={"username": username, "password": password}
            )

        if response.status_code != 201:
            logger.error(f"Error from /user: {response.text}")
            raise HTTPException(status_code=500, detail=f"Backend error: {response.text}")
        
        if (response.json())['valid'] == True:
            request.session["username"] = username
            return RedirectResponse("/", status_code=303)
        else:
            return templates.TemplateResponse("login.html", {"request": request, "login_error": "Invalid username or password."})
        
    except Exception as e:
        logger.error(f"Error in /login: {e}")
        raise HTTPException(status_code=500, detail=f"Error logging in: {e}")

@app.post("/register")
async def login(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    logger.info("Endpoint: POST /register (frontend)")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'http://fastapi-app:8080/api/v1/user',
                json={"username": username, "email": email, "password": password}
            )

        if response.status_code != 201:
            logger.error(f"Error from /user: {response.text}")
            raise HTTPException(status_code=500, detail=f"Backend error: {response.text}")
        
    except Exception as e:
        logger.error(f"Error in /register: {e}")
        raise HTTPException(status_code=500, detail=f"Error registering: {e}")

    
    request.session["username"] = username
    logger.info(f"User {username} registered successfully")

    return RedirectResponse("/", status_code=303)


# End frontend