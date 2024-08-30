import redis
import json
import os 

redis_host = os.getenv("REDIS_HOST","")
redis_port = os.getenv("REDIS_PORT","")
redis_password = os.getenv("REDIS_PASSWORD","")

redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=0)

def create(key: str, value: dict, expiry: int = None):
    try:
        redis_client.set(key, json.dumps(value))
        if expiry:
            redis_client.expire(key, expiry)  
        return True
    except Exception as e:
        return False

def read(key: str):
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        else:
            return {}
    except Exception as e:
        return {}

def update(key: str, value: dict, expiry: int = None):
    return create(key, value, expiry)  

def delete(key: str):
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        return False
