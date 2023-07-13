from enum import Enum
from pydantic import BaseModel


class ReplyType(Enum):
    TEXT = 1
    IMAGE = 2
    VIDEO = 3

    def __str__(self):
        return self.name


class Reply(BaseModel):
    type: ReplyType = None
    content: str = None

    def __init__(self, type: ReplyType, content: str):
        super().__init__()
        self.type = type
        self.content = content

    def __str__(self):
        return f"Reply(type={self.type}, content={self.content})"
