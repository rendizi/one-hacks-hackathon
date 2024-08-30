from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import EmailStr
from .models import UserCreate, User, Token, TokenData, Message, UserLogin, UserFollowing
from .utils import get_password_hash, verify_password, create_access_token, create_refresh_token,get_current_access_user,get_current_refresh_user,verify_token, verify_refresh_token
from db import users_collection
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/signup", response_model=User)
def sign_up(user: UserCreate):
    user_dict = user.dict()
    users_in_db = users_collection.find_one({"email":user_dict["email"]})
    if users_in_db is not None:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use")
    user_dict["password"] = get_password_hash(user.password)
    user_dict["preferences"] = " ."
    users_collection.insert_one(user_dict)
    return User(username=user.username, email=user.email, following=user.following, preferences=user.preferences)

@router.post("/login", response_model=Token)
def login(user_data: UserLogin):
    user = users_collection.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token_data = TokenData(email=user_data.email)
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    return {"access_token": access_token, "refresh_token": refresh_token}

async def authorize_user(token: str = Depends(oauth2_scheme)):
    try:
        # token_data = verify_token(token)
        current_user = get_current_access_user(token)
        return current_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(authorize_user)):
    user = users_collection.find_one({"email": current_user.email})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return User(username=user["username"], email=user["email"], preferences=user["preferences"], following=user["following"])

@router.post("/refresh-token", response_model=Token)
def refresh_token(req: Request):
    try:
        refreshToken = req.headers.get("Authorization")
        token_data = verify_refresh_token(refreshToken)
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)
        return {"access_token": access_token, "refresh_token": refresh_token}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@router.put("/user/preferences", response_model=Message)
def put_preferences(preferences: str,current_user: User = Depends(authorize_user)):
    user = users_collection.find_one({"email": current_user.email})
    if user is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = users_collection.update_one(
        {"email": current_user.email},
        {"$set": {"preferences": preferences}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update preferences")
    
    return {"message": "Preferences updated successfully"}

@router.put("/user/followings", response_model=Message)
def put_followings(followigs: UserFollowing, current_user: User = Depends(authorize_user)):
    user = users_collection.find_one({"email": current_user.email})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    current_followings = user.get("following", [])
    updated_followings = list(set(current_followings + followigs.following))
    
    result = users_collection.update_one(
        {"email": current_user.email},
        {"$set": {"following": updated_followings}}
    )
    
    return {"message": "Followings updated successfully"}

@router.delete("/user/followings/{following}", response_model=Message)
def delete_following(following: str, current_user: User = Depends(authorize_user)):
    user = users_collection.find_one({"email": current_user.email})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    current_followings = user.get("following", [])
    
    if following not in current_followings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Following not found in user's followings")

    updated_followings = [f for f in current_followings if f != following]
    
    result = users_collection.update_one(
        {"email": current_user.email},
        {"$set": {"following": updated_followings}}
    )
    
    return {"message": "Following removed successfully"}