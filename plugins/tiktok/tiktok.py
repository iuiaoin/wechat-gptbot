import re
import os
import time
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
            event.reply = Reply(ReplyType.TEXT, self.tiktok())
            event.bypass()

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "Use the command #tiktok(or whatever you like set with command field in the config) to get a wonderful video"

    def tiktok() -> str:
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
                    url = "http:" + str(videos_url[0])
                    res = requests.get(url, timeout=5, verify=False)
                    dir = os.path.dirname(os.path.abspath(__file__))
                    path = os.path.join(dir, "video")
                    videos_name = int(time.time() * 1000)
                    # Name the picture in the form of a timeline
                    with open(f"{path}\\{videos_name}.mp4", "wb+") as f:
                        f.write(res.content)
                        f.close()
                    video_path = os.path.abspath(f"{path}\\{videos_name}.mp4")
                    msg = video_path.replace("\\", "\\\\")
                else:
                    msg = "Error: Unrecognized URL connection"
                    logger.error(msg)
            else:
                msg = f"Abnormal site status, request: {response.status_code}"
        except Exception as e:
            logger.error(f"Error: {e}")
            msg = f"Video api call error: {e}"
        return msg
