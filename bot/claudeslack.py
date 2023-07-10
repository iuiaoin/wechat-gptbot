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
# HUMAN_PROMPT = "\n\nHuman:"
# AI_PROMPT = "\n\nAssistant:"

import asyncio

session_fitst_send_ts = {}
session_last_send_ts = {}
session_chatts = {}

from slack_claude.slack import client


async def claude_slack_chat(body,fitst_send_ts,last_send_ts,chatts):
    await client.open_channel()
    send_ts = await client.chat(body,last_send_ts)
    if fitst_send_ts == None:
        print('first get '+send_ts)
        fitst_send_ts = send_ts
    msg =  await client.get_reply(fitst_send_ts,chatts)
    return (fitst_send_ts,send_ts,msg['text'],msg['ts'])

@singleton
class ClaudeSlackBot:
    def __init__(self):
        self.what = None

    def reply(self,wx,sender_id, query, context,room_id = None,sender_name= None):
        logger.info(f"[Slack] Query={query}")
        # if context.get("type", None) == const.CREATE_IMAGE:
        #     trans = translate(query.replace("draw",""))
        #     return self.reply_img(trans)
        # else:
        try:
            session_id = context.get("session_id")

            clear_session_command = conf().get("clear_session_command") or "#clear session"
            clear_all_sessions_command = conf().get("clear_all_sessions_command") or "#clear all sessions"
            query_key_command = conf().get("query_key_command") or "#query key"
    
            # if query == clear_session_command:
            #     Session.clear_session(session_id)
            #     return Reply(ReplyType.TEXT, "The session has been cleared")
            # elif query == clear_all_sessions_command:
            #     Session.clear_all_session()
            #     return Reply(ReplyType.TEXT, "All sessions have been cleared")
            # elif query == query_key_command:
            #     return Reply(ReplyType.TEXT, QueryKey.get_key())
            session = Session.build_session_query(query, session_id)
            if len(session) == 2:
                query = session[0]['content']+"。"+query
            asyncio.run(self.async_reply_text(wx,sender_id,room_id,sender_name,query,session_id))
        except Exception as e:
            logger.exception(f"[ClaudeAPI] Exception: {e}")


    async def reply_text(self, query,session_id):
        logger.info(f'reply_text')                        
        try:
            first_send_ts,send_ts,text,chat_ts = await claude_slack_chat(query,session_fitst_send_ts.get(session_id),session_last_send_ts.get(session_id),session_chatts.get(session_id))
            session_fitst_send_ts[session_id] = first_send_ts
            session_last_send_ts[session_id] = send_ts
            session_chatts[session_id] = chat_ts
        except Exception as e:
            result = {"completion_tokens": 0, "content": "Please ask me again"}
            logger.exception(f"[ClaudeAPI] Exception: {e}")
            return result   

        return {
            "total_tokens": 1,
            "completion_tokens": 1,
            "content": text,
        }

    async def async_reply_text(self,wx,sender_id,room_id,sender_name, query,session_id):
        logger.info(f'async_reply_text')
        response = await self.reply_text(query,session_id)
        logger.info(f"[Slack] Response={response['content']}")
        if response["completion_tokens"] > 0:
            Session.save_session(response["content"], session_id, response["total_tokens"])
        if room_id and sender_name:
            reply_msg = wx.build_msg(response["content"], wxid=sender_id,room_id=room_id,nickname=sender_name)
            wx.ws.send(reply_msg)
        else:
            reply_msg = wx.build_msg(response["content"], wxid=sender_id)
            wx.ws.send(reply_msg)
        # return Reply(ReplyType.TEXT, response["content"])