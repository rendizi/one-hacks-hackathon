from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordBearer
from .models import FollowingsMessage
from .utils import get_followings, set_cached_followings, get_cached_followings


router = APIRouter()

@router.get("/{username}", response_model=FollowingsMessage)
def get_users_followings(username: str):
    try:
        cached_followings = get_cached_followings(username)
        if cached_followings:
            return {"following": cached_followings}

        following = get_followings(username)
        set_cached_followings(username, following)
        return {"following": following}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while getting followings",
            headers={"WWW-Authenticate": "Bearer"},
        )