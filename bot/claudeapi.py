# from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from config import conf
from common.singleton import singleton
from utils.log import logger
from common.session import Session
from utils import const
from common.reply import Reply, ReplyType
from utils.query_key import QueryKey
from draw.stable_draw import translate
import requests
import json
HUMAN_PROMPT = "\n\nHuman:"
AI_PROMPT = "\n\nAssistant:"
@singleton
class ClaudeAPIBot:
    def __init__(self):
        # openai.api_key = conf().get("openai_api_key")
        # api_base = conf().get("openai_api_base")
        # proxy = conf().get("proxy")
        # if api_base:
        #     openai.api_base = api_base
        # if proxy:
        #     openai.proxy = proxy
        # self.anthropicai = Anthropic(
        #     # defaults to os.environ.get("ANTHROPIC_API_KEY")
        #     api_key=conf().get("claude_api_key"),
        # )
        self.url = "https://api.anthropic.com/v1/complete"
        self.headers = {
            "x-api-key": conf().get("claude_api_key"),
            "content-type": "application/json"
        }
        

    def reply(self, query, context=None):
        logger.info(f"[Claude] Query={query}")
        # if context.get("type", None) == const.CREATE_IMAGE:
        #     trans = translate(query.replace("draw",""))
        #     return self.reply_img(trans)
        # else:
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
        logger.info(f"[Claude] Response={response['content']}")
        if response["completion_tokens"] > 0:
            Session.save_session(response["content"], session_id, response["total_tokens"])
        return Reply(ReplyType.TEXT, response["content"])

    # def reply_img(self, query):
    #     try:
    #         response = openai.Image.create(prompt=query, n=1, size="256x256")
    #         image_url = response["data"][0]["url"]
    #         logger.info(f"[ChatGPT] Image={image_url}")
    #         return Reply(ReplyType.IMAGE, image_url)
    #     except Exception as e:
    #         logger.error(f"[ChatGPT] Create image failed: {e}")
    #         return Reply(ReplyType.ERROR, "Image created failed")

    def reply_text(self, session):
        model = conf().get("claude_model")
        max_tokens = conf().get("claude_max_tokens")
        prompt =''
        for line in session:
            prompt += line['role'].replace('system',HUMAN_PROMPT).replace('user',HUMAN_PROMPT).replace('assistant',AI_PROMPT)
            prompt += line['content']
        prompt+=AI_PROMPT
        # logger.info(prompt)
        # temperature = conf().get("claude_temperature")
        try:
            # response = self.anthropicai.completions.create(
            #     model=model,
            #     prompt=prompt,
            #     # temperature=temperature,
            #     max_tokens_to_sample=max_tokens,
            #     # top_p=1.0,
            #     # frequency_penalty=0.0,
            #     # presence_penalty=0.0,
            # )
            data = {
                "prompt": prompt,
                "model": model,
                "max_tokens_to_sample": max_tokens,
                "stop_sequences": ["\n\nHuman:"]
            }
            
            response = requests.post(self.url, headers=self.headers, json=data)
            logger.info(response.text)
            re_data = json.loads(response.text)
            return {
                "total_tokens": 1,
                "completion_tokens": 1,
                "content": re_data['completion'],
            }
        except Exception as e:
            result = {"completion_tokens": 0, "content": "Please ask me again"}
            # if isinstance(e, openai.error.RateLimitError):
            #     logger.warn(f"[ClaudeAPI] RateLimitError: {e}")
            #     result["content"] = "Ask too frequently, please try again in 20s"
            # elif isinstance(e, openai.error.APIConnectionError):
            #     logger.warn(f"[ClaudeAPI] APIConnectionError: {e}")
            #     result["content"] = "I cannot connect the server, please check the network and try again"
            # elif isinstance(e, openai.error.Timeout):
            #     logger.warn(f"[ClaudeAPI] Timeout: {e}")
            #     result["content"] = "I didn't receive your message, please try again"
            # elif isinstance(e, openai.error.APIError):
            #     logger.warn(f"[ClaudeAPI] APIError: {e}")
            # else:
            logger.exception(f"[ClaudeAPI] Exception: {e}")
        return result
