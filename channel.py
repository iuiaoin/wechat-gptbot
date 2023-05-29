import json
import warnings

import websocket
from bs4 import BeautifulSoup
import requests

from api.openai import *
from utils import logger
from config import conf

ip = conf().get("ip")
port = conf().get("port")
admin_id = conf().get("admin_id")

# websocket._logging._logger.level = -99
requests.packages.urllib3.disable_warnings()
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

SERVER = f"ws://{ip}:{port}"
HEART_BEAT = 5005
RECV_TXT_MSG = 1
# message with quote
RECV_TXT_CITE_MSG = 49
RECV_PIC_MSG = 3
USER_LIST = 5000
GET_USER_LIST_SUCCSESS = 5001
GET_USER_LIST_FAIL = 5002
TXT_MSG = 555
PIC_MSG = 500
AT_MSG = 550
CHATROOM_MEMBER = 5010
CHATROOM_MEMBER_NICK = 5020
PERSONAL_INFO = 6500
DEBUG_SWITCH = 6000
PERSONAL_DETAIL = 6550
DESTROY_ALL = 9999
JOIN_ROOM = 10000
ATTATCH_FILE = 5003


def getid():
    return time.strftime("%Y%m%d%H%M%S")


def send(uri, data):
    base_data = {
        "id": getid(),
        "type": "null",
        "roomid": "null",
        "wxid": "null",
        "content": "null",
        "nickname": "null",
        "ext": "null",
    }
    base_data.update(data)
    url = f"http://{ip}:{port}/{uri}"
    res = requests.post(url, json={"para": base_data}, timeout=5)
    return res.json()


def get_member_nick(roomid, wxid):
    # get member's nickname in room or friend's nickname
    uri = "api/getmembernick"
    data = {"type": CHATROOM_MEMBER_NICK, "wxid": wxid, "roomid": roomid or "null"}
    respJson = send(uri, data)
    return json.loads(respJson["content"])["nick"]


def get_personal_info():
    # get your personal info
    uri = "/api/get_personal_info"
    data = {
        "id": getid(),
        "type": PERSONAL_INFO,
        "content": "op:personal info",
        "wxid": "null",
    }
    respJson = send(uri, data)
    try:
        if json.loads(respJson["content"])["wx_name"]:
            wechatBotInfo = f"""

            wechat login info:

            nickName: {json.loads(respJson["content"])['wx_name']}
            account: {json.loads(respJson["content"])['wx_code']}
            wechatId: {json.loads(respJson["content"])['wx_id']}
            startTime: {respJson['time']}
            """
        else:
            wechatBotInfo = respJson
    except Exception as e:
        logger.error("Get personal info failed!")
        logger.exception(e)
        wechatBotInfo = respJson
    logger.info(wechatBotInfo)


def handle_nick(j):
    data = j.content
    i = 0
    for d in data:
        logger.info(f"nickname:{d.nickname}")
        i += 1


def hanle_memberlist(j):
    data = j.content
    i = 0
    for d in data:
        logger.info(f"roomid:{d.roomid}")
        i += 1


def send_wxuser_list():
    """
    Get wechat contact list and wxid
    """
    qs = {
        "id": getid(),
        "type": USER_LIST,
        "content": "user list",
        "wxid": "null",
    }
    return json.dumps(qs)


def handle_wxuser_list(self):
    logger.info("Start completed!")


def heartbeat(msgJson):
    logger.info(msgJson["content"])


def on_open(ws):
    # initialize
    ws.send(send_wxuser_list())


def on_error(ws, error):
    logger.error(f"on_error:{error}")


def on_close(ws):
    logger.info("closed")


# send message function
def send_msg(msg, wxid="null", roomid=None, nickname="null"):
    if "jpg" in msg:
        msg_type = PIC_MSG
    elif roomid:
        msg_type = AT_MSG
    else:
        msg_type = TXT_MSG
    if roomid is None:
        roomid = "null"
    qs = {
        "id": getid(),
        "type": msg_type,
        "roomid": roomid,
        "wxid": wxid,
        "content": msg,
        "nickname": nickname,
        "ext": "null",
    }
    logger.info(f"send message: {qs}")
    return json.dumps(qs)


def welcome_join(msgJson):
    logger.info(f"receive message:{msgJson}")
    if "邀请" in msgJson["content"]["content"]:
        roomid = msgJson["content"]["id1"]
        nickname = msgJson["content"]["content"].split('"')[-2]
    ws.send(send_msg(f"Welcome our new friend in group", roomid=roomid, wxid="null", nickname=nickname))


def handleMsg_cite(msgJson):
    # process message with quote
    msgXml = msgJson["content"]["content"].replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    soup = BeautifulSoup(msgXml, "lxml")
    msgJson = {
        "content": soup.select_one("title").text,
        "id": msgJson["id"],
        "id1": msgJson["content"]["id2"],
        "id2": "wxid_fys2fico9put22",
        "id3": "",
        "srvid": msgJson["srvid"],
        "time": msgJson["time"],
        "type": msgJson["type"],
        "wxid": msgJson["content"]["id1"],
    }
    handle_recv_msg(msgJson)


def handle_recv_msg(msgJson):
    if "wxid" not in msgJson and msgJson["status"] == "SUCCSESSED":
        logger.info(f"消息发送成功")
        return
    logger.info(f"收到消息:{msgJson}")
    msg = ""
    keyword = msgJson["content"].replace("\u2005", "")
    if "@chatroom" in msgJson["wxid"]:
        roomid = msgJson["wxid"]  # group id
        senderid = msgJson["id1"]  # personal id
    else:
        roomid = None
        nickname = "null"
        senderid = msgJson["wxid"]  # personal id
    nickname = get_member_nick(roomid, senderid)
    if roomid:
        if keyword == "test" and senderid in admin_id.split(","):
            msg = ai_reply(keyword)
            ws.send(send_msg(msg, wxid=roomid))
            # msg = "Server is Online"
            # ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
            # Group message reply
        elif keyword == "#清除记忆":
            Session.clear_session(roomid)
            ws.send(send_msg("记忆已清除", wxid=roomid))
        elif keyword == "#清除所有":
            Session.clear_all_session()
            ws.send(send_msg("所有记忆已清除", wxid=roomid))
        elif keyword.startswith("@ChatGPT"):
            msg = OpenaiServer(keyword.replace("@ChatGPT", ""), roomid).replace("\n\n", "\n")
            # ws.send(send_msg(msg, wxid=roomid))
            ws.send(send_msg(msg, roomid=roomid, wxid=senderid, nickname=nickname))
    else:
        if keyword == "#清除记忆":
            Session.clear_session(senderid)
            ws.send(send_msg("记忆已清除", wxid=senderid))
        elif keyword == "#清除所有":
            Session.clear_all_session()
            ws.send(send_msg("所有记忆已清除", wxid=senderid))
        else:
            msg = OpenaiServer(keyword.replace("Hey", ""), senderid).replace("hey", "").replace("\n\n", "")
            ws.send(send_msg(msg, wxid=senderid))


def on_message(ws, message):
    j = json.loads(message)
    resp_type = j["type"]
    action = {
        CHATROOM_MEMBER_NICK: handle_nick,
        PERSONAL_DETAIL: handle_recv_msg,
        AT_MSG: handle_recv_msg,
        DEBUG_SWITCH: handle_recv_msg,
        PERSONAL_INFO: handle_recv_msg,
        TXT_MSG: handle_recv_msg,
        PIC_MSG: handle_recv_msg,
        CHATROOM_MEMBER: hanle_memberlist,
        RECV_PIC_MSG: handle_recv_msg,
        RECV_TXT_MSG: handle_recv_msg,
        RECV_TXT_CITE_MSG: handleMsg_cite,
        HEART_BEAT: heartbeat,
        USER_LIST: handle_wxuser_list,
        GET_USER_LIST_SUCCSESS: handle_wxuser_list,
        GET_USER_LIST_FAIL: handle_wxuser_list,
        JOIN_ROOM: welcome_join,
    }
    action.get(resp_type, print)(j)


# websocket.enableTrace(True)
ws = websocket.WebSocketApp(SERVER, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)


def bot():
    ws.run_forever()
