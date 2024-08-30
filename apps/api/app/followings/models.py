from pydantic import BaseModel, EmailStr
from typing import List

class FollowingsMessage(BaseModel):
    following: List[str]

class Token(BaseModel):
    access_token: str
    refresh_token: str

class TokenData(BaseModel):
    email: str 

class Message(BaseModel):
    message: str 