from channel import *
from pyfiglet import Figlet
from config import load_config
from termcolor import cprint


if __name__ == "__main__":
    load_config()
    cprint(Figlet(font="slant", width=2000).renderText("WeChat GPTBot"), "green")
    get_personal_info()
    bot()
