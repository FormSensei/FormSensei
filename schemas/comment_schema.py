from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    post_id: int
    text: str
    username: str

class CommentResponse(CommentCreate):
    id: int
    time_created: datetime
