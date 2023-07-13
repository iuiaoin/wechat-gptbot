import os
import time
import json
import requests
from channel.message import Message
from utils.log import logger
from utils.const import MessageType
from utils.gen import gen_id


def serialize_img(image_url: str) -> str:
    return serialize_file(image_url, "png")


def serialize_video(video_url: str) -> str:
    return serialize_file(video_url, "mp4")


def serialize_file(file_url: str, suffix: str) -> str:
    try:
        # download file
        path = os.path.abspath("./assets")
        file_name = int(time.time() * 1000)
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Raise exception if invalid response

        with open(f"{path}\\{file_name}.{suffix}", "wb+") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
            f.close()
        img_path = os.path.abspath(f"{path}\\{file_name}.{suffix}").replace(
            "\\", "\\\\"
        )
        return img_path
    except Exception as e:
        logger.error(f"[Download File Error]: {e}")


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
