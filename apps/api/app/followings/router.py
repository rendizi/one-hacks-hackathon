from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordBearer


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")