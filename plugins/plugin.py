from abc import ABC, abstractmethod
from plugins.event import Event


class Plugin(ABC):
    name = None

    def __init__(self, config: dict):
        super().__init__()
        if self.name is None:
            raise NotImplementedError("Plugin name is not defined")
        self.config = config

    @abstractmethod
    def did_receive_message(self, event: Event):
        pass

    @abstractmethod
    def will_generate_reply(self, event: Event):
        pass

    @abstractmethod
    def will_decorate_reply(self, event: Event):
        pass

    @abstractmethod
    def will_send_reply(self, event: Event):
        pass

    @abstractmethod
    def help(self, **kwargs) -> str:
        return "No help docs"
