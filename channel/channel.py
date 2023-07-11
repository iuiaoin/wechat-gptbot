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
    def generate_reply(self, context):
        pass

    @abstractmethod
    def send(self, reply, msg):
        pass
