import openai
import os
import torch
from utils.log import Logs
from config.config import openai_key
import tiktoken
import time

openai.api_key = os.getenv("OPENAI_API_KEY")
_callGPTLogger = Logs('call gpt-3.5-turbo api', '../logs/call_gpt-3.5-turbo.log')
_callADALogger = Logs('call text-embedding-ada api', '../logs/call_text-embedding-ada.log')


# tokenizer = get_tokenizer_func()
# length = len(tokenizer(your_string))

def __switch_api_generator():
    key_cursor = 0
    while True:
        yield key_cursor
        key_cursor = (key_cursor + 1) % len(openai_key)


api_key_generator = __switch_api_generator()


def __switch_api():
    global api_key_generator
    key_cursor = next(api_key_generator)
    openai.api_key = openai_key[key_cursor]


def get_tokenizer_func(model_name: str = "gpt-3.5-turbo"):
    try_times = 0
    while try_times < 11:
        try:
            tokenizer = tiktoken.encoding_for_model(model_name)
            return tokenizer.encode
        except Exception as e:
            print(e)
            try_times += 1
            __switch_api()
            time.sleep(20/len(openai_key))
    if try_times == 11:
        print("get_tokenizer_func: please check the internet connection")
        raise ConnectionError


def call_embedding_openai(prompt):
    if isinstance(prompt, str):
        prompt = [prompt]
    embedding = None
    try_times = 0
    while try_times < 11:
        try:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=prompt
            )
            _callADALogger.info("[text-embedding-ada-002]: call success")
            # embedding = [response['data'][0]['embedding']]
            embedding = [data['embedding'] for data in response['data']]
            break
        except Exception as e:
            print(e)
            _callADALogger.error(str(e))
            try_times += 1
            __switch_api()
            _callADALogger.info('switch apiKey......')
            time.sleep(20 / len(openai_key))
    if try_times == 11:
        print("call_embedding_openai: please check the internet connection")
        raise ConnectionError
    return embedding


def call_gpt3_5_turbo(message: list, max_tokens: int = 400):
    text = None
    try_times = 0
    while try_times < 11:
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo-1106',  # gpt-3.5-turbo-1106
                messages=message,
                temperature=0.1,
                max_tokens=max_tokens,
                stop=["###"]
            )
            _callGPTLogger.info(f"[gpt-3.5-turbo request cost token]: {response['usage']['total_tokens']}")
            _callGPTLogger.info(f"[gpt-3.5-turbo available tokens]: {4000 - response['usage']['total_tokens']}")
            text = response['choices'][0]['message']['content'].strip()
            break
        except Exception as e:
            print(e)
            _callGPTLogger.error(str(e))
            try_times += 1
            __switch_api()
            _callGPTLogger.info('switch apiKey......')
            time.sleep(20 / len(openai_key))
    if try_times == 11:
        print("call_gpt3_5_turbo: please check the internet connection")
        raise ConnectionError
    return text
