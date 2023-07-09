import asyncio
from os import getenv

# from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from config import conf

# load_dotenv()
# CLAUDE_BOT_ID = getenv("CLAUDE_BOT_ID")
from config import load_config
# load config
load_config()

CLAUDE_BOT_ID = conf().get("CLAUDE_BOT_ID")
print(CLAUDE_BOT_ID)
SLACK_USER_TOKEN = conf().get("SLACK_USER_TOKEN")
print(SLACK_USER_TOKEN)
class SlackClient(AsyncWebClient):

    CHANNEL_ID = conf().get("CHANNEL_ID")
    print(CHANNEL_ID)
    LAST_TS = None

    async def chat(self, text):
        if not self.CHANNEL_ID:
            raise Exception("Channel not found.")

        resp = await self.chat_postMessage(channel=self.CHANNEL_ID, text=text)
        print("c: ", resp)
        self.LAST_TS = None

    async def open_channel(self):
        if not self.CHANNEL_ID:
            response = await self.conversations_open(users=CLAUDE_BOT_ID)
            self.CHANNEL_ID = response["channel"]["id"]

    async def get_reply(self):
        for _ in range(150):
            try:
                resp = await self.conversations_history(channel=self.CHANNEL_ID, oldest=self.LAST_TS, limit=2)
                print("r: ", resp)
                msg = [msg["text"] for msg in resp["messages"] if msg["user"] == CLAUDE_BOT_ID]
                if msg and not msg[-1].endswith("Typing…_"):
                    return msg[-1]
            except (SlackApiError, KeyError) as e:
                print(f"Get reply error: {e}")

            await asyncio.sleep(1)

        raise Exception("Get replay timeout")

    async def get_stream_reply(self):
        l = 0
        for _ in range(150):
            try:
                resp = await self.conversations_history(channel=self.CHANNEL_ID, oldest=self.LAST_TS, limit=2)
                msg = [msg["text"] for msg in resp["messages"] if msg["user"] == CLAUDE_BOT_ID]
                if msg:
                    last_msg = msg[-1]
                    more = False
                    if msg[-1].endswith("Typing…_"):
                        last_msg = str(msg[-1])[:-11] # remove typing…
                        more = True
                    diff = last_msg[l:]
                    if diff == "":
                        continue
                    l = len(last_msg)
                    yield diff
                    if not more:
                        break
            except (SlackApiError, KeyError) as e:
                print(f"Get reply error: {e}")

            await asyncio.sleep(2)

client = SlackClient(token=SLACK_USER_TOKEN)

if __name__ == '__main__':
    async def server():
        await client.open_channel()
        while True:
            prompt = input("You: ")
            await client.chat(prompt)

            reply = await client.get_reply()
            print(f"Claude: {reply}\n--------------------")

    asyncio.run(server())