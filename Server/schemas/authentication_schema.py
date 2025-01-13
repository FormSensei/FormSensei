from pydantic import BaseModel, EmailStr

class Authentication(BaseModel):
    username: str
    password: str

class AuthenticationResponse(BaseModel):
    valid: bool