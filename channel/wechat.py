import json
import warnings
import websocket
from bs4 import BeautifulSoup
import requests
from utils.log import logger
from utils import const
import os
from bot.bot import Bot
from common.singleton import singleton
from config import conf
from utils.check import check_prefix, is_wx_account
from common.reply import ReplyType, Reply
from channel.message import Message
from utils.api import get_personal_info, send_image, send_file
from utils.const import MessageType
from utils.serialize import serialize_img, serialize_text, serialize_video
from plugins.manager import PluginManager
from common.context import ContextType, Context
from plugins.event import EventType, Event
from channel.channel import Channel


@singleton
class WeChatChannel(Channel):
    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        warnings.filterwarnings("ignore")
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"
        self.personal_info = get_personal_info()
        self.ws = websocket.WebSocketApp(
            const.SERVER,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def startup(self):
        logger.info("App startup successfully!")
        self.ws.run_forever()

    def on_message(self, ws, message):
        raw_msg = json.loads(message)
        msg_type = raw_msg["type"]
        handlers = {
            MessageType.AT_MSG.value: self.handle_message,
            MessageType.TXT_MSG.value: self.handle_message,
            MessageType.PIC_MSG.value: self.handle_message,
            MessageType.RECV_PIC_MSG.value: self.handle_message,
            MessageType.RECV_TXT_MSG.value: self.handle_message,
            MessageType.RECV_TXT_CITE_MSG.value: self.handle_cite_message,
            MessageType.HEART_BEAT.value: self.noop,
        }
        handlers.get(msg_type, logger.info)(raw_msg)

    def noop(self, raw_msg):
        pass

    def handle_cite_message(self, raw_msg):
        xml_msg = (
            raw_msg["content"]["content"]
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )
        soup = BeautifulSoup(xml_msg, "lxml")
        cooked_msg = {
            "content": soup.select_one("title").text,
            "id": raw_msg["id"],
            "id1": raw_msg["content"]["id2"],
            "id2": "",
            "id3": "",
            "srvid": raw_msg["srvid"],
            "time": raw_msg["time"],
            "type": raw_msg["type"],
            "wxid": raw_msg["content"]["id1"],
        }
        self.handle_message(cooked_msg)

    def handle_message(self, raw_msg):
        if "wxid" not in raw_msg and raw_msg["status"] == const.SUCCESS:
            logger.info("message sent successfully")
            return
        # ignore message sent by self
        if raw_msg["id2"] == self.personal_info["wx_id"]:
            logger.info("message sent by self, ignore")
            return
        msg = Message(raw_msg, self.personal_info)
        logger.info(f"message received: {msg}")
        e = PluginManager().emit(
            Event(EventType.DID_RECEIVE_MESSAGE, {"channel": self, "message": msg})
        )
        if e.is_bypass:
            return self.send(e.reply, e.message)
        if e.message.is_group:
            self.handle_group(e.message)
        else:
            self.handle_single(e.message)

    def handle_group(self, msg: Message):
        session_independent = conf().get("chat_group_session_independent")
        context = Context()
        context.session_id = msg.sender_id if session_independent else msg.room_id
        if msg.is_at:
            query = msg.content.replace(f"@{msg.receiver_name}", "", 1).strip()
            context.query = query
            create_image_prefix = conf().get("create_image_prefix")
            match_prefix = check_prefix(query, create_image_prefix)
            if match_prefix:
                context.type = ContextType.CREATE_IMAGE
            self.handle_reply(msg, context)

    def handle_single(self, msg: Message):
        # ignore message sent by public/subscription account
        if not is_wx_account(msg.sender_id):
            logger.info("message sent by public/subscription account, ignore")
            return
        context = Context()
        context.session_id = msg.sender_id
        query = msg.content
        single_chat_prefix = conf().get("single_chat_prefix")
        if single_chat_prefix is not None and len(single_chat_prefix) > 0:
            match_chat_prefix = check_prefix(query, single_chat_prefix)
            if match_chat_prefix is not None:
                query = query.replace(match_chat_prefix, "", 1).strip()
            else:
                logger.info("your message is not start with single_chat_prefix, ignore")
                return
        context.query = query
        create_image_prefix = conf().get("create_image_prefix")
        match_image_prefix = check_prefix(query, create_image_prefix)
        if match_image_prefix:
            context.type = ContextType.CREATE_IMAGE
        self.handle_reply(msg, context)

    def decorate_reply(self, reply: Reply, msg: Message) -> Reply:
        if reply.type == ReplyType.TEXT:
            group_chat_reply_prefix = conf().get("group_chat_reply_prefix", "")
            group_chat_reply_suffix = conf().get("group_chat_reply_suffix", "")
            single_chat_reply_prefix = conf().get("single_chat_reply_prefix", "")
            single_chat_reply_suffix = conf().get("single_chat_reply_suffix", "")
            reply_text = reply.content
            if msg.is_group:
                reply_text = (
                    group_chat_reply_prefix + reply_text + group_chat_reply_suffix
                )
            else:
                reply_text = (
                    single_chat_reply_prefix + reply_text + single_chat_reply_suffix
                )
            reply.content = reply_text
        return reply

    def handle_reply(self, msg: Message, context: Context):
        e1 = PluginManager().emit(
            Event(
                EventType.WILL_GENERATE_REPLY,
                {"channel": self, "message": msg, "context": context},
            )
        )
        if e1.is_bypass:
            return self.send(e1.reply, e1.message)

        rawReply = Bot().reply(e1.context)

        e2 = PluginManager().emit(
            Event(
                EventType.WILL_DECORATE_REPLY,
                {
                    "channel": self,
                    "message": e1.message,
                    "context": e1.context,
                    "reply": rawReply,
                },
            )
        )
        if e2.is_bypass:
            return self.send(e2.reply, e2.message)

        reply = self.decorate_reply(rawReply, msg)

        e3 = PluginManager().emit(
            Event(
                EventType.WILL_SEND_REPLY,
                {
                    "channel": self,
                    "message": e2.message,
                    "context": e2.context,
                    "reply": reply,
                },
            )
        )
        self.send(e3.reply, e3.message)

    def send(self, reply: Reply, msg: Message):
        if reply is None:
            return
        if reply.type == ReplyType.IMAGE:
            img_path = serialize_img(reply.content)
            wx_id = msg.room_id if msg.is_group else msg.sender_id
            send_image(img_path, wx_id)
        elif reply.type == ReplyType.VIDEO:
            file_path = serialize_video(reply.content)
            wx_id = msg.room_id if msg.is_group else msg.sender_id
            send_file(file_path, wx_id)
        else:
            reply_msg = serialize_text(reply.content, msg)
            self.ws.send(reply_msg)

    def on_open(self, ws):
        logger.info("[Websocket] connected")

    def on_close(self, ws):
        logger.info("[Websocket] disconnected")

    def on_error(self, ws, error):
        logger.error(f"[Websocket] Error: {error}")
