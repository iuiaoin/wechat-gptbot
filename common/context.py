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
    system_prompt: str = conf().get("role_desc")
