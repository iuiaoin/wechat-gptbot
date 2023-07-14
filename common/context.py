from pydantic import BaseModel
from enum import Enum
from config import conf


class ContextType(Enum):
    CREATE_TEXT = 1
    CREATE_IMAGE = 2

    def __str__(self):
        return self.name


class Context(BaseModel):
    session_id: str = None
    type: ContextType = ContextType.CREATE_TEXT
    query: str = None
    system_prompt: str = None

    def __init__(self):
        super().__init__()
        self.system_prompt = conf().get("role_desc")
