from db import users_collection
from instagrapi.types import Story
from services.gemini import video_vision
from services.chatgpt import image_text_vision

def get_all_users():
    try:
        users = users_collection.find()
        user_list = list(users)
        return user_list
    except Exception as e:
        print(f"An error occurred while fetching users: {e}")
        return []

