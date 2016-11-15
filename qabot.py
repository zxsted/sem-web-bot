import json
import requests
import time
import urllib

import config

from qa import answer_question 

import logging

# set up logging
logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)


TOKEN = config.bot_token
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def answer_all(updates):
    for update in updates["result"]:
        logger.debug(update)
        try: 
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message("Let me see", chat)
            response = answer_question(text)
            if response["status"] == "answered":
                logger.info(response["answer"])
                send_message(response["answer"][0], chat)
            else:
                send_message("Sorry :( I'm still learning. Please ask me something easier", chat)
        except Exception as e:
            print(e)
            logger.info(e)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = str(text)
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            answer_all(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()