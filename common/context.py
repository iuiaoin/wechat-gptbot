from pydantic import BaseModel
from enum import Enum


class ContextType(Enum):
    CREATE_TEXT = 1
    CREATE_IMAGE = 2

    def __str__(self):
        return self.name


class Context(BaseModel):
    session_id: str = None
    type: ContextType = ContextType.CREATE_TEXT
    query: str = None
