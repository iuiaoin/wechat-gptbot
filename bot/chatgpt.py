import openai
from config import conf
from utils.log import logger
from common.session import Session
from common.reply import Reply, ReplyType
from common.context import ContextType, Context


class ChatGPTBot:
    def __init__(self):
        openai.api_key = conf().get("openai_api_key")
        api_base = conf().get("openai_api_base")
        proxy = conf().get("proxy")
        if api_base:
            openai.api_base = api_base
        if proxy:
            openai.proxy = proxy
        self.name = self.__class__.__name__
        self.args = {
            "model": conf().get("model"),
            "temperature": conf().get("temperature"),
        }

    def reply(self, context: Context) -> Reply:
        query = context.query
        logger.info(f"[{self.name}] Query={query}")
        if context.type == ContextType.CREATE_IMAGE:
            return self.reply_img(query)
        else:
            session_id = context.session_id
            session = Session.build_session_query(context)
            response = self.reply_text(session)
            logger.info(f"[{self.name}] Response={response['content']}")
            if response["completion_tokens"] > 0:
                Session.save_session(
                    response["content"], session_id, response["total_tokens"]
                )
            return Reply(ReplyType.TEXT, response["content"])

    def reply_img(self, query) -> Reply:
        create_image_size = conf().get("create_image_size", "512x512")
        create_image_model = conf().get("create_image_model", "dall-e-3")
        create_image_style = conf().get("create_image_style", "vivid")
        create_image_quality = conf().get("create_image_quality", "standard")
        
        try:
            response = openai.Image.create(prompt=query, model=create_image_model, n=1, size=create_image_size,
                style=create_image_style, quality=create_image_quality)
            image_url = response["data"][0]["url"]
            logger.info(f"[{self.name}] Image={image_url}")
            return Reply(ReplyType.IMAGE, image_url)
        except Exception as e:
            logger.error(f"[{self.name}] Create image failed: {e}")
            return Reply(ReplyType.TEXT, "Image created failed")

    def reply_text(self, session):
        try:
            response = openai.ChatCompletion.create(
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
