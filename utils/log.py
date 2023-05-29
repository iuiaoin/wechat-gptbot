import logging
import sys


def _get_logger():
    log = logging.getLogger("log")
    log.setLevel(logging.INFO)
    console_handle = logging.StreamHandler(sys.stdout)
    console_handle.setFormatter(
        logging.Formatter(
            "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    log.addHandler(console_handle)
    return log


# log handler
logger = _get_logger()
