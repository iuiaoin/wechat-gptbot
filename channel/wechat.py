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


@singleton
class WeChatChannel:
    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        warnings.filterwarnings("ignore")
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"
        self.personal_info = self.get_personal_info()
        self.ws = websocket.WebSocketApp(
            const.SERVER,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def startup(self):
        self.ws.run_forever()
        logger.info("App startup successfully!")

    def on_message(self, ws, message):
        msg = json.loads(message)
        msg_type = msg["type"]
        handlers = {
            const.AT_MSG: self.handle_message,
            const.TXT_MSG: self.handle_message,
            const.PIC_MSG: self.handle_message,
            const.RECV_PIC_MSG: self.handle_message,
            const.RECV_TXT_MSG: self.handle_message,
            const.RECV_TXT_CITE_MSG: self.handle_cite_message,
        }
        handlers.get(msg_type, logger.info)(msg)

    def handle_cite_message(self, msg):
        xml_msg = msg["content"]["content"].replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        soup = BeautifulSoup(xml_msg, "lxml")
        cooked_msg = {
            "content": soup.select_one("title").text,
            "id": msg["id"],
            "id1": msg["content"]["id2"],
            "id2": "",
            "id3": "",
            "srvid": msg["srvid"],
            "time": msg["time"],
            "type": msg["type"],
            "wxid": msg["content"]["id1"],
        }
        self.handle_message(cooked_msg)

    def handle_message(self, msg):
        # "SUCCSESSED" should be a typo in the hook server😂
        if "wxid" not in msg and msg["status"] == "SUCCSESSED":
            logger.info("message sent successfully")
            return
        logger.info(f"message received: {msg}")
        if "@chatroom" in msg["wxid"]:
            self.handle_group(msg)
        else:
            self.handle_single(msg)

    def handle_group(self, msg):
        room_id = msg["wxid"]
        sender_id = msg["id1"]
        query = msg["content"].strip()
        personal_name = self.personal_info["wx_name"]
        context = dict()
        context["session_id"] = room_id
        sender_name = self.get_sender_name(room_id, sender_id)
        if query.startswith(f"@{personal_name}"):
            reply_text = ChatGPTBot().reply(query.replace(f"@{personal_name}", ""), room_id)
            reply_msg = self.build_msg(reply_text, wxid=sender_id, room_id=room_id, nickname=sender_name)
            self.ws.send(reply_msg)

    def handle_single(self, msg):
        sender_id = msg["wxid"]
        query = msg["content"].strip()
        reply_text = ChatGPTBot().reply(query, sender_id)
        reply_msg = self.build_msg(reply_text, wxid=sender_id)
        self.ws.send(reply_msg)

    def build_msg(content, wxid="null", room_id=None, nickname="null"):
        if room_id:
            msg_type = const.AT_MSG
        else:
            msg_type = const.TXT_MSG
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

    def get_personal_info(self):
        uri = "/api/get_personal_info"
        data = {
            "id": gen_id(),
            "type": const.PERSONAL_INFO,
            "content": "op:personal info",
            "wxid": "null",
        }
        try:
            response = self.fetch(uri, data)
            content = json.loads(response["content"])
            logger.info(
                f"""
                wechat login info:
                
                nickName: {content['wx_name']}
                account: {content['wx_code']}
                wechatId: {content['wx_id']}
                startTime: {response['time']}
                """
            )
            return content
        except Exception as e:
            logger.error("Get personal info failed!")
            logger.exception(e)

    # get sender's nickname in group chat
    def get_sender_name(self, room_id, wxid):
        uri = "api/getmembernick"
        data = {"type": const.CHATROOM_MEMBER_NICK, "wxid": wxid, "roomid": room_id or "null"}
        response = self.fetch(uri, data)
        return json.loads(response["content"])["nick"]

    def fetch(self, uri, data):
        base_data = {
            "id": gen_id(),
            "type": "null",
            "roomid": "null",
            "wxid": "null",
            "content": "null",
            "nickname": "null",
            "ext": "null",
        }
        base_data.update(data)
        url = f"http://{const.IP}:{const.PORT}/{uri}"
        response = requests.post(url, json={"para": base_data}, timeout=5)
        return response.json()

    def on_open(self):
        logger.info("[Websocket] connected")

    def on_close(self):
        logger.info("[Websocket] disconnected")

    def on_error(self, ws, error):
        logger.error(f"[Websocket] Error: {error}")
