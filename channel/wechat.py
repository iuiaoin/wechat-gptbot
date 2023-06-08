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
        logger.info("App startup successfully!")
        self.ws.run_forever()

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
            const.HEART_BEAT: self.noop,
        }
        handlers.get(msg_type, logger.info)(msg)

    def noop(self, msg):
        pass

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
        if "wxid" not in msg and msg["status"] == const.SUCCESS:
            logger.info("message sent successfully")
            return
        # ignore message sent by self
        if msg["id2"] == self.personal_info["wx_id"]:
            logger.info("message sent by self, ignore")
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
            cooked_query = query.replace(f"@{personal_name}", "").strip()
            create_image_prefix = conf().get("create_image_prefix")
            match_prefix = check_prefix(cooked_query, create_image_prefix)
            if match_prefix:
                context["type"] = const.CREATE_IMAGE
            reply = ChatGPTBot().reply(cooked_query, context)
            if reply.type == ReplyType.IMAGE:
                self.send_img(reply.content, room_id)
            else:
                reply_msg = self.build_msg(reply.content, wxid=sender_id, room_id=room_id, nickname=sender_name)
                self.ws.send(reply_msg)

    def handle_single(self, msg):
        sender_id = msg["wxid"]
        # ignore message sent by public/subscription account
        if not is_wx_account(sender_id):
            logger.info("message sent by public/subscription account, ignore")
            return
        context = dict()
        context["session_id"] = sender_id
        query = msg["content"].strip()
        create_image_prefix = conf().get("create_image_prefix")
        match_prefix = check_prefix(query, create_image_prefix)
        if match_prefix:
            context["type"] = const.CREATE_IMAGE
        reply = ChatGPTBot().reply(query, context)
        if reply.type == ReplyType.IMAGE:
            self.send_img(reply.content, sender_id)
        else:
            reply_msg = self.build_msg(reply.content, wxid=sender_id)
            self.ws.send(reply_msg)

    def send_img(self, content, wxid):
        try:
            # download image
            path = os.path.abspath("./assets")
            img_name = int(time.time() * 1000)
            response = requests.get(content, stream=True)
            response.raise_for_status()  # Raise exception if invalid response

            with open(f"{path}\\{img_name}.png", "wb+") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                f.close()
            img_path = os.path.abspath(f"{path}\\{img_name}.png").replace("\\", "\\\\")

            data = {
                "id": gen_id(),
                "type": const.PIC_MSG,
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

    def on_open(self, ws):
        logger.info("[Websocket] connected")

    def on_close(self, ws):
        logger.info("[Websocket] disconnected")

    def on_error(self, ws, error):
        logger.error(f"[Websocket] Error: {error}")
