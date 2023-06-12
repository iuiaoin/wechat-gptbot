import openai
from config import conf
from common.singleton import singleton
from utils.log import logger
from common.session import Session
from utils import const
from common.reply import Reply, ReplyType
from utils.queryKey import QueryKey


@singleton
class ChatGPTBot:
    def __init__(self):
        openai.api_key = conf().get("openai_api_key")
        api_base = conf().get("openai_api_base")
        proxy = conf().get("proxy")
        if api_base:
            openai.api_base = api_base
        if proxy:
            openai.proxy = proxy

    def reply(self, query, context=None):
        logger.info(f"[ChatGPT] Query={query}")
        if context.get("type", None) == const.CREATE_IMAGE:
            return self.reply_img(query)
        else:
            session_id = context.get("session_id")
            clear_session_command = conf().get("clear_session_command") or "#clear session"
            clear_all_sessions_command = conf().get("clear_all_sessions_command") or "#clear all sessions"
            query_key_command = conf().get("query_key_command") or "#query key"
            if query == clear_session_command:
                Session.clear_session(session_id)
                return Reply(ReplyType.TEXT, "The session has been cleared")
            elif query == clear_all_sessions_command:
                Session.clear_all_session()
                return Reply(ReplyType.TEXT, "All sessions have been cleared")
            elif query == query_key_command:
                return Reply(ReplyType.TEXT, QueryKey.get_key())
            session = Session.build_session_query(query, session_id)
            response = self.reply_text(session)
            logger.info(f"[ChatGPT] Response={response['content']}")
            if response["completion_tokens"] > 0:
                Session.save_session(response["content"], session_id, response["total_tokens"])
            return Reply(ReplyType.TEXT, response["content"])

    def reply_img(self, query):
        try:
            response = openai.Image.create(prompt=query, n=1, size="256x256")
            image_url = response["data"][0]["url"]
            logger.info(f"[ChatGPT] Image={image_url}")
            return Reply(ReplyType.IMAGE, image_url)
        except Exception as e:
            logger.error(f"[ChatGPT] Create image failed: {e}")
            return Reply(ReplyType.ERROR, "Image created failed")

    def reply_text(self, session):
        model = conf().get("model")
        max_tokens = conf().get("max_tokens")
        temperature = conf().get("temperature")
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=session,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            return {
                "total_tokens": response["usage"]["total_tokens"],
                "completion_tokens": response["usage"]["completion_tokens"],
                "content": response.choices[0]["message"]["content"],
            }
        except Exception as e:
            result = {"completion_tokens": 0, "content": "Please ask me again"}
            if isinstance(e, openai.error.RateLimitError):
                logger.warn(f"[ChatGPT] RateLimitError: {e}")
                result["content"] = "Ask too frequently, please try again in 20s"
            elif isinstance(e, openai.error.APIConnectionError):
                logger.warn(f"[ChatGPT] APIConnectionError: {e}")
                result["content"] = "I cannot connect the server, please check the network and try again"
            elif isinstance(e, openai.error.Timeout):
                logger.warn(f"[ChatGPT] Timeout: {e}")
                result["content"] = "I didn't receive your message, please try again"
            elif isinstance(e, openai.error.APIError):
                logger.warn(f"[ChatGPT] APIError: {e}")
            else:
                logger.exception(f"[ChatGPT] Exception: {e}")
        return result
