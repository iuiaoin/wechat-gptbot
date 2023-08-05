from bot.chatgpt import ChatGPTBot
import openai
import litellm
from litellm import completion
from utils.log import logger
from config import conf
import os

class liteLLMChatGPTBot(ChatGPTBot):
    def __init__(self):
        openai.api_key = conf().get("openai_api_key")
        os.environ['OPENAI_API_KEY'] = openai.api_key # litellm reads env variables for keys

        # extra litellm configs:
        api_base = conf().get("openai_api_base")
        proxy = conf().get("proxy")
        if api_base:
            litellm.api_base = api_base
        if proxy:
            openai.proxy = proxy
        self.name = self.__class__.__name__
        self.args = {
            "model": conf().get("model"),
            "temperature": conf().get("temperature"),
        }

    def reply_text(self, session):
        try:
            response = completion(
                messages=session,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                **self.args,
            )
            return {
                "total_tokens": response["usage"]["total_tokens"],
                "completion_tokens": response["usage"]["completion_tokens"],
                "content": response.choices[0]["message"]["content"],
            }
        except Exception as e:
            result = {"completion_tokens": 0, "content": "Please ask me again"}
            if isinstance(e, openai.error.RateLimitError):
                logger.warn(f"[{self.name}] RateLimitError: {e}")
                result["content"] = "Ask too frequently, please try again in 20s"
            elif isinstance(e, openai.error.APIConnectionError):
                logger.warn(f"[{self.name}] APIConnectionError: {e}")
                result[
                    "content"
                ] = "I cannot connect the server, please check the network and try again"
            elif isinstance(e, openai.error.Timeout):
                logger.warn(f"[{self.name}] Timeout: {e}")
                result["content"] = "I didn't receive your message, please try again"
            elif isinstance(e, openai.error.APIError):
                logger.warn(f"[{self.name}] APIError: {e}")
            else:
                logger.exception(f"[{self.name}] Exception: {e}")
        return result
