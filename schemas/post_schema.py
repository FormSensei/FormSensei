from pydantic import BaseModel
from typing import Optional

class PostCreate(BaseModel):
    image: str
    text: str
    user: str

class PostResponse(BaseModel):
    id: int
    image: str
    text: str
    user: str
    timestamp: str