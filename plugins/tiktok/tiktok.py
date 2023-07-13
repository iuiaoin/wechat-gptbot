import re
import requests
from plugins import register, Plugin, Event, logger, Reply, ReplyType


@register
class TikTok(Plugin):
    name = "tiktok"

    def did_receive_message(self, event: Event):
        pass

    def will_generate_reply(self, event: Event):
        query = event.context.query
        if query == self.config.get("command"):
            event.reply = self.reply()
            event.bypass()

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "Use the command #tiktok(or whatever you like set with command field in the config) to get a wonderful video"

    def reply(self) -> Reply:
        reply = Reply(ReplyType.TEXT, "Failed to get tiktok videos")
        try:
            response = requests.get(
                "https://tucdn.wpon.cn/api-girl/", timeout=5, verify=False
            )
            if response.status_code == 200:
                videos_url = re.findall(
                    '<video src="(.*?)" muted controls preload="auto"',
                    response.text,
                    re.S,
                )
                if len(videos_url) > 0:
                    reply = Reply(ReplyType.VIDEO, "http:" + str(videos_url[0]))
                else:
                    logger.error("Error: Unrecognized URL connection")
            else:
                logger.error(f"Abnormal site status, request: {response.status_code}")
        except Exception as e:
            logger.error(f"Video api call error: {e}")
        return reply
