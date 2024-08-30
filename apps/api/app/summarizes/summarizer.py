from instagrapi import Client
from .utils import get_all_users
import os 
from services.chatgpt import image_text_vision
from services.gemini import video_vision
from services.mailer import send_summarize
from services.shotstack import generate_video
from services.aws import upload_to_aws
from db import summarizes_collection
from datetime import datetime
from services.redis import create,read,update,delete
import json 

bot_username = os.getenv("BOT_ACCOUNT_USERNAME", "")
bot_password = os.getenv("BOT_ACCOUNT_PASSWORD", "")

def summarize():
    users = get_all_users()
    cl = Client()
    cl.login(username=bot_username, password=bot_password)
    for user in users:
        email = user["email"]
        followings = user["following"]
        preferences = user["preferences"]
        medias_for_video = []
        user_stories_summarizes = []
        for following in followings:
            todays_prev_stories_summarizes = []
            this_weeks_prev_stories_summarizes = read(following)
            user_id = cl.user_id_from_username(following)
            stories = cl.user_stories(user_id=user_id)
            chat = [] 
            for story in stories:
                if story.id in this_weeks_prev_stories_summarizes:
                    summarize = this_weeks_prev_stories_summarizes[story.id]
                else:
                    if story.video_url:
                        prompt = "I have a video from an " + following + "'s Instagram story. Your task is to determine if it contains any interesting or relevant information about the person's life or news. If it does, summarize this information in 1 short sentence. If the video content is not related to the person's personal life, not interesting or important activities/news, return the following response: 'Nothing interesting'. Give a logically connected summary based on previous stories (if empty, don't say it's empty, give a result only based on video or return an empty response): " + ",".join(str(item) for item in todays_prev_stories_summarizes) + ". Last 7 days stories: " + ",".join(str(item) for item in this_weeks_prev_stories_summarizes) + ". Don't repeat what is already summarized and in old stories. Maximum tokens: 75, write it as simple as possible, like people would say, use simple words. Response should be in the following JSON format: {\"description\": string, \"addIt\": bool, \"length\": int}. If you think that this story should be added to a short recap video, set `addIt` to true; otherwise, set it to false. If `addIt` is true, specify the length in seconds it should be in the clip as \"length\"."
                        response = video_vision(str(story.video_url))
                        summarize = response.candidates[0].content.__dict__
                        summarize["type"] = "video"
                        summarize["src"] = str(story.video_url)
                    else:
                        prompt = "I have a video from an " + following + "'s Instagram story. Your task is to determine if it contains any interesting or relevant information about the person's life or news. If it does, summarize this information in 1 short sentence. If the video content is not related to the person's personal life, not interesting or important activities/news, return the following response: 'Nothing interesting'. Give a logically connected summary based on previous stories (if empty, don't say it's empty, give a result only based on video or return an empty response): " + ",".join(str(item) for item in todays_prev_stories_summarizes) + ". Last 7 days stories: " + ",".join(str(item) for item in this_weeks_prev_stories_summarizes) + ". Don't repeat what is already summarized and in old stories. Maximum tokens: 75, write it as simple as possible, like people would say, use simple words. Response should be in the following JSON format: {\"description\": string, \"addIt\": bool, \"length\": int}. If you think that this story should be added to a short recap video, set `addIt` to true; otherwise, set it to false. If `addIt` is true, specify the length in seconds it should be in the clip as \"length\"."
                        chat.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": str(story.thumbnail_url) ,
                                    },
                                },
                            ]
                        })
                        response = image_text_vision(chat, "")
                        content = response.message.content
                        try:
                            summarize = json.loads(content)
                            chat.append(response)
                            summarize["type"] = "image"
                            summarize["src"] = str(story.thumbnail_url)  
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                    summarize["username"] = following
                        
                if "addIt" in summarize and summarize['addIt'] == True:
                    medias_for_video.append(summarize)
                if "addIt" in summarize and summarize['description'] != "Nothing interesting.":
                    todays_prev_stories_summarizes.append(summarize)
                create(summarize["src"], summarize, 86400)
            prompt = "You are given array of storieses summarize. I am very busy so give the most interesting ones, make them shorter without losing an idea. Maximum symbols-100, don't use markup symbols. Response should be like 1 text, no need to divide into ordered/unordered list. If is is empty or there is information not interesting and not related with someone's life- return 'Nothing interesting'. Write simple. Response should be in json format- {\"description\":string}. User's preferences: " + preferences
            chat = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": ",".join(json.dumps(item) for item in todays_prev_stories_summarizes)},
                ]
                }]
            response = image_text_vision(chat, prompt)
            content = response.message.content
            try:
                summarize = json.loads(content)
                summarize_of_all_users_stories = summarize["description"]
                create(following, summarize_of_all_users_stories, 86400*7)
                if summarize_of_all_users_stories != "Nothing interesting":
                    user_stories_summarizes.append(summarize_of_all_users_stories)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                
                    
        print("User stories summarizes",user_stories_summarizes) 
        url = generate_video(medias_for_video)
        send_summarize(email, user_stories_summarizes)
        aws_url = upload_to_aws(url)
        summarizes_collection.insert_one({
            "email": email,
            "video_url": aws_url,
            "summarizes": user_stories_summarizes,
            "date": datetime.now().strftime('%Y-%m-%d')
        })        

