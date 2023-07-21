from clauderevised.claude import ClaudeAPIWrapper
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
import asyncio

session_conversation_uuids = {}


@singleton
class ClaudeWebBot:
    def __init__(self):
        # "sessionKey=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"

        # organization_uuid = 'b2a66215-c7ea-4844-b9bf-ea5b9b100c86'

        # conversations = api.get_chat_conversations(organization_uuid)
        # print(conversations)

        # conversation_uuid = conversations[0]["uuid"]
        self.fu = None

    def initsession(self):
        self.session_key = conf().get("claude_web_sessionKey")
        logger.info(self.session_key)
        
        self.api = ClaudeAPIWrapper(self.session_key)

        organizations = self.api.get_organizations()
        logger.info(organizations)

        self.organization_uuid = organizations[0]["uuid"]
    
    def reply(self,wx,sender_id, query, context,room_id = None,sender_name= None):
        logger.info(f"[ClaudeWeb] Query={query}")
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
            logger.exception(f"[ClaudeWeb] Exception: {e}")   

    async def async_reply_text(self,wx,sender_id,room_id,sender_name, query,session_id):
        logger.info(f'async_reply_text')
        # response = await self.reply_text(query,session_id)

        attachments = []
        conversation_uuid = session_conversation_uuids.get(session_id)
        if conversation_uuid == None:
            conversation_uuid = self.api.add_chat_conversation(self.organization_uuid,query[-10:] )['uuid']
            session_conversation_uuids[session_id] = conversation_uuid
        print('conversation_uuid:'+conversation_uuid)

        response = self.api.send_message(self.organization_uuid, conversation_uuid, query,
                                    attachments)
        total_msg =''
        for message in response:
            total_msg += message
            # print(message, end='', flush=True)

        logger.info(f"[ClaudeWeb] Response={total_msg}")
        # if response["completion_tokens"] > 0:
        #     Session.save_session(response["content"], session_id, response["total_tokens"])
        if room_id and sender_name:
            reply_msg = wx.build_msg(total_msg, wxid=sender_id,room_id=room_id,nickname=sender_name)
            wx.ws.send(reply_msg)
        else:
            reply_msg = wx.build_msg(total_msg, wxid=sender_id)
            wx.ws.send(reply_msg)
        # return Reply(ReplyType.TEXT, response["content"])            