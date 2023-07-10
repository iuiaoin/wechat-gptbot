import asyncio
from os import getenv

# from dotenv import load_dotenv
# from slack_sdk.web.async_client import AsyncWebClient
# from slack_sdk.errors import SlackApiError
from config import conf
from utils.log import logger
import json
import requests
import aiohttp

# load_dotenv()
# CLAUDE_BOT_ID = getenv("CLAUDE_BOT_ID")
from config import load_config
# load config
load_config()

CLAUDE_BOT_ID = conf().get("CLAUDE_BOT_ID")
print(CLAUDE_BOT_ID)
SLACK_USER_TOKEN = conf().get("SLACK_USER_TOKEN")
print(SLACK_USER_TOKEN)
class SlackClient():

    CHANNEL_ID = conf().get("CHANNEL_ID")
    print(CHANNEL_ID)
    # msg_ts  = None
    # thread_ts  = None
    _send_url = 'https://slack.com/api/chat.postMessage'
    headers = {
        "Authorization": f"Bearer {SLACK_USER_TOKEN}",
        "content-type": "application/json"
    }

    async def make_post_request(self,url, json,headers):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json,headers=headers) as response:
                # 处理响应对象
                response_data = await response.json()  # 解析响应体为JSON数据
                return response_data

    async def make_get_request(self,url,headers):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                # 处理响应对象
                response_data = await response.json()  # 解析响应体为JSON数据
                return response_data                

    def GetResponseUrl(self,ts, oldest, channel):
        return "https://slack.com/api/conversations.replies?channel=" + (channel) + "&ts=" + (ts) + "&oldest=" +(oldest or "")
        
    async def chat(self, text,last_send_ts):
        if not self.CHANNEL_ID:
            raise Exception("Channel not found.")

        data = {
            "channel": conf().get("CHANNEL_ID"),
            "text": f'<@{CLAUDE_BOT_ID}> '+text,
            "thread_ts": last_send_ts
        }
        
        resp = await self.make_post_request(self._send_url, json=data,headers=self.headers)
        # resp = await self.chat_postMessage(channel=conf().get("CHANNEL_ID"), text=f'<@{CLAUDE_BOT_ID}> '+text,thread_ts=last_send_ts)
        logger.info("c: "+ str(resp))
        return resp['message']['ts']

    async def open_channel(self):
        # if not self.CHANNEL_ID:
        #     response = await self.conversations_open(users=CLAUDE_BOT_ID)
        #     self.CHANNEL_ID = response["channel"]["id"]
        print('open_channel')

    async def get_reply(self,fitst_send_ts,chat_ts):
        print("get chat_ts:"+(chat_ts or ""))
        for _ in range(150):
            try:
                get_url = self.GetResponseUrl(channel=conf().get("CHANNEL_ID"), ts=fitst_send_ts ,oldest=chat_ts)
                resp = await self.make_get_request(get_url, headers=self.headers)
                # resp = await self.conversations_history(channel=conf().get("CHANNEL_ID"), ts=fitst_send_ts ,oldest=chat_ts, limit=6)
                # logger.info("res: "+ str(resp))
                get_msg = [msg for msg in resp['messages'] if (msg['user'] == CLAUDE_BOT_ID and (not '*Please note:*' in msg['text'] ) and (not '_Oops!*' in msg['text'] )  )]
                if get_msg:
                    logger.info("filter: "+ get_msg[-1]['text'])
                else:
                    logger.info("filter: ")
                    
                if get_msg and not get_msg[-1]['text'].endswith("Typing…_"):
                    return get_msg[-1]
            except Exception as e:
                logger.exception(f"Get reply error: {e}")

            await asyncio.sleep(1)

        raise Exception("Get replay timeout")

    # async def get_stream_reply(self):
    #     l = 0
    #     for _ in range(150):
    #         try:
    #             resp = await self.conversations_history(channel=self.CHANNEL_ID,ts=self.msg_ts ,oldest=self.thread_ts, limit=2)
    #             msg = [msg["text"] for msg in resp["messages"] if msg["user"] == CLAUDE_BOT_ID]
    #             if msg:
    #                 last_msg = msg[-1]
    #                 more = False
    #                 if msg[-1].endswith("Typing…_"):
    #                     last_msg = str(msg[-1])[:-11] # remove typing…
    #                     more = True
    #                 diff = last_msg[l:]
    #                 if diff == "":
    #                     continue
    #                 l = len(last_msg)
    #                 yield diff
    #                 if not more:
    #                     break
    #         except (SlackApiError, KeyError) as e:
    #             print(f"Get reply error: {e}")

    #         await asyncio.sleep(2)

client = SlackClient()

# if __name__ == '__main__':
#     async def server():
#         await client.open_channel()
#         while True:
#             prompt = input("You: ")
#             await client.chat(prompt)

#             reply = await client.get_reply()
#             print(f"Claude: {reply}\n--------------------")

#     asyncio.run(server())