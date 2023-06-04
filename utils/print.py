from pyfiglet import Figlet
from termcolor import cprint


def color_print(text, color="green"):
    content = Figlet(font="slant", width=2000).renderText(text)
    cprint(content, color)
