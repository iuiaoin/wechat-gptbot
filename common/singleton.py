def singleton(cls):
    instances = {}

    class Singleton(cls):
        def __new__(cls):
            if cls not in instances:
                instances[cls] = super(Singleton, cls).__new__(cls)
            return instances[cls]

    Singleton.__name__ = cls.__name__
    return Singleton
