from pydantic import BaseModel, EmailStr
from typing import List

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    following: List[str] = []
    preferences: str = ""

class UserLogin(BaseModel):
    email: EmailStr
    password: str 

class UserFollowing(BaseModel):
    following: List[str]

class UserInDB(UserCreate):
    hashed_password: str

class User(BaseModel):
    username: str
    email: EmailStr
    following: List[str]
    preferences: str 

class Token(BaseModel):
    access_token: str
    refresh_token: str

class TokenData(BaseModel):
    email: str 

class Message(BaseModel):
    message: str 