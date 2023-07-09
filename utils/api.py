import const
from gen import gen_id
import requests
import json
from log import logger


def fetch(uri, data):
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
def get_sender_name(room_id, sender_id):
    uri = "api/getmembernick"
    data = {
        "type": const.CHATROOM_MEMBER_NICK,
        "wxid": sender_id,
        "roomid": room_id or "null",
    }
    response = fetch(uri, data)
    return json.loads(response["content"])["nick"]
