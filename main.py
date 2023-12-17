import requests
from urllib.parse import quote_plus
from config import TG_TOKEN, API_TOKEN 
import re
BASE_URL = f'https://api.telegram.org/bot{TG_TOKEN}/'


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
    text = re.escape(text)
    params = {'chat_id': chat_id, 'text': text,"parse_mode":"MarkdownV2"}
    response = requests.post(url, params=params)
    return response.json()

def process_message(update):
    chat_id = update['message']['chat']['id']
    user_message = update['message']['text']
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

    while True:
        updates = get_updates(offset)

        if updates:
            for update in updates:
                process_message(update)
                offset = update['update_id'] + 1

if __name__ == '__main__':
    main();
