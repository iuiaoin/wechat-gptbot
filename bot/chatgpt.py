import openai
from config import conf
from common.singleton import singleton


@singleton
class ChatGPTBot:
    def __init__(self):
        openai.api_key = conf().get("openai_api_key")
        proxy = conf().get("proxy")
        if proxy:
            openai.proxy = proxy
