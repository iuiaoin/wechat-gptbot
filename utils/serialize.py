import os
import time
import json
import requests
from channel.message import Message
from utils.log import logger
from utils.const import MessageType
from utils.gen import gen_id


def serialize_img(image_url: str) -> str:
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
        return img_path
    except Exception as e:
        logger.error(f"[Download Image Error]: {e}")


def serialize_text(text: str, msg: Message) -> str:
    msg_type = MessageType.AT_MSG.value if msg.is_group else MessageType.TXT_MSG.value
    msg = {
        "id": gen_id(),
        "type": msg_type,
        "roomid": msg.room_id or "null",
        "wxid": msg.sender_id or "null",
        "content": text,
        "nickname": msg.sender_name or "null",
        "ext": "null",
    }
    return json.dumps(msg)
