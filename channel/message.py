from pydantic import BaseModel
from enum import Enum
from utils.api import get_sender_name


class MessageType(Enum):
    RECV_TXT_MSG = 1
    RECV_PIC_MSG = 3
    RECV_TXT_CITE_MSG = 49
    PIC_MSG = 500
    AT_MSG = 550
    TXT_MSG = 555
    USER_LIST = 5000
    GET_USER_LIST_SUCCESS = 5001
    GET_USER_LIST_FAIL = 5002
    ATTACH_FILE = 5003
    HEART_BEAT = 5005
    CHATROOM_MEMBER = 5010
    CHATROOM_MEMBER_NICK = 5020
    PERSONAL_INFO = 6500
    PERSONAL_DETAIL = 6550
    DEBUG_SWITCH = 6000
    DESTROY_ALL = 9999
    JOIN_ROOM = 10000


class Message(BaseModel):
    room_id: str = None
    sender_id: str = None
    sender_name: str = None
    receiver_id: str = None
    receiver_name: str = None
    content: str = None
    type: MessageType = None
    is_group: bool = False
    is_at: bool = False
    create_time: str = None
    at_list: str = None
    _raw_msg: dict = None

    def __init__(self, msg, info):
        super().__init__()
        self._raw_msg = msg
        self.receiver_id = info["wx_id"]
        self.receiver_name = info["wx_name"]
        self.content = msg["content"].strip()
        self.type = msg["type"]
        self.create_time = msg["time"]
        if "@chatroom" in msg["wxid"]:
            self.is_group = True
            self.room_id = msg["wxid"]
            self.sender_id = msg["id1"]
            self.at_list = msg["id3"]
            self.is_at = self.receiver_id in self.at_list
        else:
            self.is_group = False
            self.sender_id = msg["wxid"]
        self.sender_name = get_sender_name(self.room_id, self.sender_id)

    def __str__(self):
        return f"Message(room_id={self.room_id}, sender_id={self.sender_id}, sender_name={self.sender_name}, receiver_id={self.receiver_id}, receiver_name={self.receiver_name}, content={self.content}, type={self.type}, is_group={self.is_group}, create_time={self.create_time}, at_list={self.at_list})"
