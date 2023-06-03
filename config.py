import json
import os
from utils.log import logger

config = {}


def load_config():
    global config
    config_path = "config.json"
    if not os.path.exists(config_path):
        raise Exception("Config file is not exist, please create config.json according to config.template.json")

    config_str = read_file(config_path)
    # deserialize json string to dict
    config = json.loads(config_str)
    logger.info(f"Load config: {config}")


def read_file(path):
    with open(path, mode="r", encoding="utf-8") as f:
        return f.read()


def conf():
    return config
