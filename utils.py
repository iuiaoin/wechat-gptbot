from termcolor import cprint
import time


def output(self):
    if "error" in self or "ERROR" in self:
        color = "red"
    else:
        color = "green"
    time_now = time.strftime("%Y-%m-%d %X")
    cprint(f"[{time_now}]:{self}", color)
