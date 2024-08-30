from openai import OpenAI
import os 

openai_api_key = os.getenv("OPENAI_API_KEY","")

client = OpenAI(api_key=openai_api_key)

def image_text_vision(chat, system_prompt):
    system_message = {
        "role": "system",
        "content": [
            {"type": "text", "text":system_prompt}
        ]
    }
    messages = [system_message] + chat
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_object"},
        max_tokens=300,
    )
    return response.choices[0]
