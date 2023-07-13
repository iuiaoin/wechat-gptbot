from enum import Enum
from typing import Callable


class Emitter:
    def __init__(self):
        self.__events__ = {}

    # subscribe event
    def on(self, type: Enum, fn: Callable) -> None:
        if type not in self.__events__:
            self.__events__[type] = []
        if not self.has(type, fn):
            self.__events__[type].append(fn)

    # unsubscribe event
    def off(self, type: Enum, fn: Callable) -> None:
        listeners = self.__events__.get(type)
        if listeners is not None and len(listeners) > 0:
            listeners.remove(fn)

    # check if the function has subscribed the event
    def has(self, type: Enum, fn: Callable) -> bool:
        listeners = self.__events__.get(type)
        if listeners is None or len(listeners) == 0:
            return False
        return fn in listeners

    # emit event
    def emit(self, type: Enum, *args, **kwargs) -> None:
        listeners = self.__events__.get(type)
        if listeners is not None and len(listeners) > 0:
            for fn in listeners:
                fn(*args, **kwargs)

    # subscribe event and unsubscribe after once
    def once(self, type: Enum, fn: Callable) -> None:
        def once_fn(*args, **kwargs):
            fn(*args, **kwargs)
            self.off(type, once_fn)

        self.on(type, once_fn)
