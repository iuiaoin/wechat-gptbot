from abc import ABC, abstractmethod


class Channel(ABC):
    @abstractmethod
    def handle_message(self, msg):
        pass

    @abstractmethod
    def handle_group(self, msg):
        pass

    @abstractmethod
    def handle_single(self, msg):
        pass

    @abstractmethod
    def decorate_reply(self, reply, msg):
        pass

    @abstractmethod
    def handle_reply(self, msg, context):
        pass

    @abstractmethod
    def send(self, reply, msg):
        pass
