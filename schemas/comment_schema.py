from pydantic import BaseModel
from typing import Optional

class CommentCreate(BaseModel):
    post_id: int
    text: str
    user: str

class CommentResponse(CommentCreate):
    id: int
    time_created: str
