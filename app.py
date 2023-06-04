from channel.wechat import WeChatChannel
from config import load_config
from utils.log import logger
from utils.print import color_print


if __name__ == "__main__":
    try:
        # load config
        load_config()

        # print banner
        color_print("WeChat GPTBot")

        # start wechat channel
        WeChatChannel().startup()
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)
