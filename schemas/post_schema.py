from pydantic import BaseModel
from datetime import datetime

class PostCreate(BaseModel):
    username: str
    text: str
    image: str
    id: int

class PostBase(BaseModel):
    username: str
    text: str
    image: str


class PostResponse(BaseModel):
    id: int
    username: str
    text: str
    image: str
    time_created: datetime