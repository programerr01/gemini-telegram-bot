import requests
from urllib.parse import quote_plus
from copy_config import TG_TOKEN, API_TOKEN
import re
import base64
import os

BASE_URL = f'https://api.telegram.org/bot{TG_TOKEN}/'
IMG_PATH = f"https://api.telegram.org/file/bot{TG_TOKEN}/"
def get_pro_llm_response(img,prompt):

    base64_img = base64.b64encode(img).decode("utf-8");

    data = {
    "contents": [
        {
            "parts": [
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": base64_img
                    }
                },
                {"text":prompt},

            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.4,
        "topK": 32,
        "topP": 1,
        "maxOutputTokens": 4096,
        "stopSequences": []
    },
    "safetySettings": [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
        ]
    }
    headers = {"Content-Type":"application/json"}
    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key=' + API_TOKEN
    response = requests.post(url, json=data, headers=headers)
    print(response.json())
    return response.json()['candidates'][0]['content']['parts'][0]['text'];


def get_llm_response(prompt):
    headers = {"Content-Type": "application/json"};

    params = {"key":API_TOKEN};

    json_data = {
    'contents': [
        {
            'parts': [{"text":str(prompt) }],
        },
    ],
    'generationConfig': {
        'temperature': 0.9,
        'topK': 1,
        'topP': 1,
        'maxOutputTokens': 2048,
        'stopSequences': [],
    },
    'safetySettings': [
        {
            'category': 'HARM_CATEGORY_HARASSMENT',
            'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
        },
        {
            'category': 'HARM_CATEGORY_HATE_SPEECH',
            'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
        },
        {
            'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
            'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
        },
        {
            'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
            'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
        },
    ],
    }
    response = requests.post(
    'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
    params=params,
    headers=headers,
    json=json_data,
    )
    return response.json()['candidates'][0]['content']['parts'][0]['text']




def getWelcomeMessage():
    return """Welcome to the gemini bot,
you can get response from gemini api directly in telegram"""

def send_message(chat_id, text):
    url = BASE_URL + 'sendMessage';
    print(text)
    text = re.escape(text).replace("!","\\!");
    params = {'chat_id': chat_id, 'text': text,"parse_mode":"MarkdownV2"}
    response = requests.post(url, params=params)
    return response.json()

def process_message(update):
    chat_id = update['message']['chat']['id']
    print(update)
    user_message = update['message']['caption']

    message = update.get("message",{});

    if "photo" in message:
        file_id = message['photo'][-1]['file_id']
        width = message['photo'][-1]['width']
        height = message['photo'][-1]['height']


        download_url =  f"{BASE_URL}getFile?file_id={file_id}"
        file_info = requests.get(download_url).json()['result']
        file_path = file_info['file_path']
        image_url = f"{IMG_PATH}{file_path}"
        file_path = file_path.split("/")[-1]
        response = requests.get(image_url)
        # with open(file_path, 'wb') as f:
        #     f.write(response.content)

        response_text = get_pro_llm_response(response.content,user_message);
        print(send_message(chat_id,response_text))
        return;

    print(chat_id);
    response_text = "";
    if(user_message == "/start"):
        response_text = getWelcomeMessage();
    else:
        response_text = get_llm_response(user_message);
    # Send a response to the user
    print(send_message(chat_id, response_text))

def get_updates(offset=None):
    url = BASE_URL + 'getUpdates'
    params = {'offset': offset, 'timeout': 100}
    response = requests.get(url, params=params)
    return response.json()['result']

def main():
    offset = None;print("Started Running....")
    checking_offset = True;
    while True:
        updates = get_updates(offset)

        if updates:
            for update in updates:
                if(not checking_offset):
                    process_message(update)
                offset = update['update_id'] + 1

        checking_offset = False;
if __name__ == '__main__':
    main()
