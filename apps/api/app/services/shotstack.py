import requests
from typing import List
import random
import json 
import os 
import time 

def generate_video(assets: List[dict]):
    request = generate_video_structure(assets)
    try:
        request_json = json.dumps(request)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Error serializing request to JSON: {e}")
    
    api_key = os.getenv("SHOTSTACK_API_KEY")
    if not api_key:
        raise EnvironmentError("SHOTSTACK_API_KEY not set in environment")
    
    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        response = requests.post(
            "https://api.shotstack.io/edit/stage/render",
            data=request_json,
            headers=headers
        )
        response.raise_for_status() 
    except requests.RequestException as e:
        raise RuntimeError(f"Request failed: {e}")
    
    try:
        result = response.json()
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Error parsing JSON response: {e}")
    
    if not result.get("success", False):
        raise RuntimeError(f"Failed to queue render: {result.get('message', 'No message provided')}")
    
    response_data = result.get("response")
    if not response_data:
        raise ValueError("Invalid response format: 'response' key not found")
    
    render_id = response_data.get("id")
    if not render_id or not isinstance(render_id, str):
        raise ValueError("Render ID not found or not a string")
    
    url = get_url(render_id)
    return url 


def generate_video_structure(assets: List[dict]):
    start = 0
    clips = []
    effects = ["zoomIn", "slideUp", "slideLeft", "zoomOut", "slideDown", "slideRight"]
    
    for ind, clip in enumerate(assets):
        temp_clip = {
            "asset": {
                "type": clip["type"],
                "src": clip['src'],
            },
            "start": start,
            "length": clip.get("length", 3),
            "effect": random.choice(effects),
            "transition": {
                "in": "fade" if ind == 0 else None,
                "out": "fade"
            }
        }
        
        if clip["type"] == "video":
            temp_clip["asset"]["trim"] = clip.get("trim", 0)
            temp_clip["asset"]["volume"] = clip.get("volume", 1)
        
        clips.append(temp_clip)
        start += clip.get("length", 3)  
    
    result_request = {
        "output": {
            "format": "mp4",
            "size": {
                "width": 720,
                "height": 1280
            }
        },
        "timeline": {
            "tracks": [
                {"clips": clips},
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "audio",
                                "src": "https://shotstack-assets.s3-ap-southeast-2.amazonaws.com/music/freepd/advertising.mp3",
                                "effect": "fadeOut",
                                "volume": 1
                            },
                            "start": 0,
                            "length": "end"
                        }
                    ]
                }
            ]
        }
    }
    
    return result_request


def get_url(render_id):
    while True:
        url = f"https://api.shotstack.io/edit/stage/render/{render_id}"
        
        try:
            headers = {"x-api-key": os.getenv("SHOTSTACK_API_KEY")}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() 
        except requests.RequestException as e:
            raise RuntimeError(f"Error sending request: {e}")
        
        try:
            response_data = response.json()
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Error decoding response body: {e}")
        
        success = response_data.get("success", False)
        if not isinstance(success, bool):
            raise ValueError("Invalid response format, 'success' field not found or not a boolean")

        if success:
            url = response_data.get("response", {}).get("url")
            if url and isinstance(url, str):
                return url
            else:
                time.sleep(25)
        else:
            print("Render was not successful. Retrying in 25 seconds...")
            time.sleep(25)