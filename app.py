from channel import *
from pyfiglet import Figlet
from utils import logger
from config import load_config
from termcolor import cprint


def main():
    logger.info("wechat-gptbot run ....")
    get_personal_info()
    bot()


if __name__ == "__main__":
    load_config()
    f = Figlet(font="slant", width=2000)
    cprint(f.renderText("WeChat GPTBot"), "green")
    main()
