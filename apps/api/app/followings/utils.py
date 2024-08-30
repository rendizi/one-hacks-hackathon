from instagrapi import Client
import os 
from datetime import datetime, timedelta
from typing import Dict, Any


bot_username = os.getenv("BOT_ACCOUNT_USERNAME", "")
bot_password = os.getenv("BOT_ACCOUNT_PASSWORD", "")

cache: Dict[str, Any] = {}
CACHE_EXPIRY = timedelta(minutes=15)
MAX_CACHE_SIZE = 50

def get_cached_followings(username: str):
    if username in cache:
        cached_data, timestamp = cache[username]
        if datetime.now() - timestamp < CACHE_EXPIRY:
            return cached_data
        else:
            del cache[username]  
    return None

def set_cached_followings(username: str, data: Any):
    if len(cache) >= MAX_CACHE_SIZE:
        oldest_key = min(cache, key=lambda k: cache[k][1])
        del cache[oldest_key]
    cache[username] = (data, datetime.now())


def get_followings(username: str):
    cl = Client()
    cl.login(bot_username, bot_password)

    user_id = cl.user_id_from_username(username=username)
    followings = cl.user_following(user_id=user_id, amount=0)
    
    usernames = [user.username for user in followings.values()]
    return usernames