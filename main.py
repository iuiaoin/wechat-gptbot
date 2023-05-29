from channel import *
from utils import *
from pyfiglet import Figlet


def main():
    output("wechat-gptbot run ....")
    get_personal_info()
    bot()


if __name__ == "__main__":
    f = Figlet(font="slant", width=2000)
    cprint(f.renderText("WECHAT GPTBOT"), "green")
    main()
