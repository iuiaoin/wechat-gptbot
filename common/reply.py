from enum import Enum


class ReplyType(Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    ERROR = "ERROR"

    def __str__(self):
        return self.name


class Reply:
    def __init__(self, type: ReplyType = None, content=None):
        self.type = type
        self.content = content

    def __str__(self):
        return f"Reply(type={self.type}, content={self.content})"
