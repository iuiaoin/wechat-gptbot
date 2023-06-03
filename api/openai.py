import openai
from common.session import Session
from utils.log import logger
from config import conf


def OpenaiServer(msg=None, session_id=""):
    openai.api_key = conf().get("openai_api_key")
    model = conf().get("model")
    res = ""
    try:
        if msg is None:
            logger.error("msg is None")
            res = ""
        else:
            session = Session.build_session_query(msg, session_id)
            response = openai.ChatCompletion.create(
                model=model,
                messages=session,
                temperature=0.6,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
            )
            total_tokens = response["usage"]["total_tokens"]
            completion_tokens = response["usage"]["completion_tokens"]
            res = response.choices[0]["message"]["content"]
            if completion_tokens > 0:
                Session.save_session(res, session_id, total_tokens)
    except Exception as e:
        logger.error("Server error!")
        logger.exception(e)
        res = e
    return res
