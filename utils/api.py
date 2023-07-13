from utils import const
from utils.gen import gen_id
import requests
import json
from utils.log import logger
from utils.const import MessageType


def fetch(path, data):
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
    url = f"http://{const.IP}:{const.PORT}/{path}"
    response = requests.post(url, json={"para": base_data}, timeout=5)
    return response.json()


def get_personal_info():
    path = "/api/get_personal_info"
    data = {
        "type": MessageType.PERSONAL_INFO.value,
        "content": "op:personal info",
    }
    try:
        response = fetch(path, data)
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
def get_sender_name(room_id, sender_id):
    path = "api/getmembernick"
    data = {
        "type": MessageType.CHATROOM_MEMBER_NICK.value,
        "wxid": sender_id,
        "roomid": room_id or "null",
    }
    response = fetch(path, data)
    return json.loads(response["content"])["nick"]


def send_txt(msg, wx_id):
    path = "api/sendtxtmsg"
    data = {
        "type": MessageType.TXT_MSG.value,
        "content": msg,
        "wxid": wx_id,
    }
    response = fetch(path, data)
    if response["status"] == const.SUCCESS:
        logger.info("text sent successfully")
    else:
        logger.error(f"[Server Error]: {response.text}")


def send_image(img_path, wx_id):
    path = "api/sendpic"
    data = {
        "type": MessageType.PIC_MSG.value,
        "content": img_path,
        "wxid": wx_id,
    }
    response = fetch(path, data)
    if response["status"] == const.SUCCESS:
        logger.info("image sent successfully")
    else:
        logger.error(f"[Server Error]: {response.text}")


def send_file(file_path, wx_id):
    path = "api/sendattatch"
    data = {
        "type": MessageType.ATTACH_FILE.value,
        "content": file_path,
        "wxid": wx_id,
    }
    response = fetch(path, data)
    if response["status"] == const.SUCCESS:
        logger.info("file sent successfully")
    else:
        logger.error(f"[Server Error]: {response.text}")
