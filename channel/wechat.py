import json
import warnings
import websocket
from bs4 import BeautifulSoup
import requests
from utils.log import logger
from utils import const
import os
from utils.gen import gen_id
from bot.chatgpt import ChatGPTBot
from common.singleton import singleton
from config import conf
from utils.check import check_prefix, is_wx_account
from common.reply import ReplyType
import time
from channel.message import Message
from utils.api import get_personal_info
from utils.const import MessageType


@singleton
class WeChatChannel:
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
        # did receive message
        if msg.is_group:
            self.handle_group(msg)
        else:
            self.handle_single(msg)

    def handle_group(self, msg: Message):
        session_independent = conf().get("chat_group_session_independent")
        context = dict()
        context["session_id"] = msg.sender_id if session_independent else msg.room_id
        if msg.is_at:
            query = msg.content.replace(f"@{msg.receiver_name}", "", 1).strip()
            create_image_prefix = conf().get("create_image_prefix")
            match_prefix = check_prefix(query, create_image_prefix)
            if match_prefix:
                context["type"] = const.CREATE_IMAGE
            reply = ChatGPTBot().reply(query, context)
            if reply.type == ReplyType.IMAGE:
                self.send_img(reply.content, msg.room_id)
            else:
                reply_msg = self.build_msg(
                    reply.content,
                    wxid=msg.sender_id,
                    room_id=msg.room_id,
                    nickname=msg.sender_name,
                )
                self.ws.send(reply_msg)

    def handle_single(self, msg: Message):
        # ignore message sent by public/subscription account
        if not is_wx_account(msg.sender_id):
            logger.info("message sent by public/subscription account, ignore")
            return
        context = dict()
        context["session_id"] = msg.sender_id
        query = msg.content
        single_chat_prefix = conf().get("single_chat_prefix")
        if single_chat_prefix is not None and len(single_chat_prefix) > 0:
            match_chat_prefix = check_prefix(query, single_chat_prefix)
            if match_chat_prefix is not None:
                query = query.replace(match_chat_prefix, "", 1).strip()
            else:
                logger.info("your message is not start with single_chat_prefix, ignore")
                return
        create_image_prefix = conf().get("create_image_prefix")
        match_image_prefix = check_prefix(query, create_image_prefix)
        if match_image_prefix:
            context["type"] = const.CREATE_IMAGE
        reply = ChatGPTBot().reply(query, context)
        if reply.type == ReplyType.IMAGE:
            self.send_img(reply.content, msg.sender_id)
        else:
            reply_msg = self.build_msg(reply.content, wxid=msg.sender_id)
            self.ws.send(reply_msg)

    def send_img(self, image_url, wxid):
        try:
            # download image
            path = os.path.abspath("./assets")
            img_name = int(time.time() * 1000)
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # Raise exception if invalid response

            with open(f"{path}\\{img_name}.png", "wb+") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                f.close()
            img_path = os.path.abspath(f"{path}\\{img_name}.png").replace("\\", "\\\\")

            data = {
                "id": gen_id(),
                "type": MessageType.PIC_MSG.value,
                "roomid": "null",
                "content": img_path,
                "wxid": wxid,
                "nickname": "null",
                "ext": "null",
            }
            url = f"http://{const.IP}:{const.PORT}/api/sendpic"
            res = requests.post(url, json={"para": data}, timeout=5)
            if res.status_code == 200 and res.json()["status"] == const.SUCCESS:
                logger.info("image sent successfully")
            else:
                logger.error(f"[Server Error]: {res.text}")
        except Exception as e:
            logger.error(f"[Download Image Error]: {e}")

    def build_msg(self, content, wxid="null", room_id=None, nickname="null"):
        if room_id:
            msg_type = MessageType.AT_MSG.value
        else:
            msg_type = MessageType.TXT_MSG.value
        if room_id is None:
            room_id = "null"
        msg = {
            "id": gen_id(),
            "type": msg_type,
            "roomid": room_id,
            "wxid": wxid,
            "content": content,
            "nickname": nickname,
            "ext": "null",
        }
        return json.dumps(msg)

    def on_open(self, ws):
        logger.info("[Websocket] connected")

    def on_close(self, ws):
        logger.info("[Websocket] disconnected")

    def on_error(self, ws, error):
        logger.error(f"[Websocket] Error: {error}")
