import os
import time
import requests
import google.generativeai as genai
import uuid

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def download_media(url, local_filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(local_filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

def generate_random_filename(extension='mp4'):
    return f"temp_video_{uuid.uuid4().hex}.{extension}"

def video_vision(url):
    video_file_name = generate_random_filename()
    
    download_media(url, video_file_name)

    video_file = genai.upload_file(path=video_file_name)

    while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(f"Video processing failed with state: {video_file.state.name}")

    prompt = "Summarize this video. Then create a quiz with an answer key based on the information in the video."

    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    response = model.generate_content([video_file, prompt])

    os.remove(video_file_name)
    
    return response


