from bot.chatgpt import ChatGPTBot
import openai
import litellm
from litellm import completion
from utils.log import logger
from config import conf


class LiteLLMChatGPTBot(ChatGPTBot):
    def __init__(self):
        api_key = conf().get("openai_api_key")
        model = conf().get("model", "gpt-3.5-turbo")
        api_base = conf().get("openai_api_base")
        proxy = conf().get("proxy")

        if model in litellm.cohere_models:
            litellm.cohere_key = api_key
        elif model in litellm.anthropic_models:
            litellm.anthropic_key = api_key
        else:
            litellm.openai_key = api_key

        if api_base:
            litellm.api_base = api_base
        if proxy:
            openai.proxy = proxy
        self.name = self.__class__.__name__
        self.args = {
            "model": model,
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
