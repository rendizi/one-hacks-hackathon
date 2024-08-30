from pydantic import BaseModel, EmailStr
from typing import List

class FollowingsMessage(BaseModel):
    following: List[str]
