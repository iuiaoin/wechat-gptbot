from datetime import datetime, timedelta


class ExpiredDict(dict):
    def __init__(self, expired_duration):
        super().__init__()
        self.expired_duration = expired_duration

    def __getitem__(self, key):
        value, expired_time = super().__getitem__(key)
        if datetime.now() > expired_time:
            del self[key]
            raise KeyError(f"expired {key}")
        self.__setitem__(key, value)
        return value

    def __setitem__(self, key, value):
        expired_time = datetime.now() + timedelta(seconds=self.expired_duration)
        super().__setitem__(key, (value, expired_time))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
