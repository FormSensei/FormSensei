from pydantic import BaseModel

class PostCreate(BaseModel):
    user: str
    text: str
    image: str
    id: int

class PostBase(BaseModel):
    user: str
    text: str
    image: str


class PostResponse(BaseModel):
    id: int
    user: str
    text: str
    image: str
    time_created: str