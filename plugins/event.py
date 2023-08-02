from enum import Enum
from pydantic import BaseModel
from common.context import Context
from common.reply import Reply
from channel.message import Message
from channel.channel import Channel


class EventType(Enum):
    DID_RECEIVE_MESSAGE = 1  # receive message
    WILL_GENERATE_REPLY = 2  # generate reply
    WILL_DECORATE_REPLY = 3  # decorate reply
    WILL_SEND_REPLY = 4  # send reply

    def __str__(self):
        return self.name


class EventAction(Enum):
    PROCEED = 1  # proceed the plugin chain
    STOP = 2  # stop the plugin chain
    BYPASS = 3  # bypass the plugin chain and default logic


class Event(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    type: EventType = None
    channel: Channel = None
    message: Message = None
    context: Context = None
    reply: Reply = None
    action: EventAction = EventAction.PROCEED

    def __init__(self, type: EventType, data: dict):
        super().__init__()
        self.type = type
        self.channel = data.get("channel")
        self.message = data.get("message")
        self.context = data.get("context")
        self.reply = data.get("reply")

    def proceed(self):
        self.action = EventAction.PROCEED

    def stop(self):
        self.action = EventAction.STOP

    def bypass(self):
        self.action = EventAction.BYPASS

    @property
    def is_proceed(self) -> bool:
        return self.action == EventAction.PROCEED

    @property
    def is_stop(self) -> bool:
        return self.action == EventAction.STOP

    @property
    def is_bypass(self) -> bool:
        return self.action == EventAction.BYPASS
