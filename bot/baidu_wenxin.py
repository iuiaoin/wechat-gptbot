# encoding:utf-8

import requests, json
from config import conf
from utils.log import logger
from common.session import Session
from common.reply import Reply, ReplyType
from common.context import ContextType, Context

from config import conf


class BaiduWenxinBot:
    def __init__(self):
        self.model = conf().get("baidu_wenxin_model") or "eb-instant"
        self.baidu_wenxin_api_key = conf().get("baidu_wenxin_api_key")
        self.baidu_wenxin_secret_key = conf().get("baidu_wenxin_secret_key")
        self.name = self.__class__.__name__

    def reply(self, context=None):
        # acquire reply content
        query = context.query
        logger.info(f"[{self.name}] Query={query}")
        if context.type == ContextType.CREATE_IMAGE:
            return self.reply_img(query)
        else:
            session_id = context.session_id
            session = Session.build_session_query(context)
            response = self.reply_text(session)
            total_tokens, completion_tokens, reply_content = (
                response["total_tokens"],
                response["completion_tokens"],
                response["content"],
            )
            logger.debug(
                "[{}] new_query={}, session_id={}, reply_cont={}, completion_tokens={}".format(
                    self.name,
                    session,
                    session_id,
                    reply_content,
                    completion_tokens,
                )
            )

            if total_tokens > 0:
                Session.save_session(
                    response["content"], session_id, response["total_tokens"]
                )
            return Reply(ReplyType.TEXT, response["content"])

    def reply_img(self, query) -> Reply:
        ok, image_url = self.create_img(query, 0)
        if ok:
            return Reply(ReplyType.IMAGE, image_url)
        else:
            logger.error(f"[{self.name}] Create image failed: {e}")
            return Reply(ReplyType.TEXT, "Image created failed")

    def reply_text(self, session, retry_count=0):
        try:
            logger.info("[{}] model={}".format(self.name,self.model))
            access_token = self.get_access_token()
            if access_token == "None":
                logger.warn(
                    "[{self.name}] access token 获取失败"
                )
                return {
                    "total_tokens": 0,
                    "completion_tokens": 0,
                    "content": 0,
                }
            url = (
                "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/"
                + self.model
                + "?access_token="
                + access_token
            )
            headers = {"Content-Type": "application/json"}
            payload = {"messages": session}
            response = requests.request(
                "POST", url, headers=headers, data=json.dumps(payload)
            )
            response_text = json.loads(response.text)
            logger.info(f"[{self.name}] response text={response_text}")
            res_content = response_text["result"]
            total_tokens = response_text["usage"]["total_tokens"]
            completion_tokens = response_text["usage"]["completion_tokens"]
            logger.info("[{}] reply={}".format(self.name,res_content))
            return {
                "total_tokens": total_tokens,
                "completion_tokens": completion_tokens,
                "content": res_content,
            }
        except Exception as e:
            logger.warn("[{}] Exception: {}".format(self.name,e))
            result = {"completion_tokens": 0, "content": "出错了: {}".format(e)}
            return result

    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.baidu_wenxin_api_key,
            "client_secret": self.baidu_wenxin_secret_key,
        }
        return str(requests.post(url, params=params).json().get("access_token"))
