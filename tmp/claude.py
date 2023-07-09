from os import getenv
from typing import Union
import asyncio

# from fastapi import FastAPI, Depends, Header, HTTPException, status
# from pydantic import BaseModel
# from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from slack import client

# app = FastAPI()
# server_token = getenv("SERVER_TOKEN")


# async def must_token(x_token: Union[str, None] = Header(None)):
#     if server_token and x_token != server_token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail={
#                 "msg": "must token",
#             }
#         )



async def chat(body):
    await client.open_channel()
    await client.chat(body)

    return {
        "claude": await client.get_reply()
    }

# add --no-buffer to see the effect of streaming
# curl -X 'POST'  --no-buffer \
#  'http://127.0.0.1:8088/claude/stream_chat' \
#  -H 'accept: text/plain' \
#  -H 'Content-Type: application/json' \
#  -d '{
#  "prompt": "今天天气很不错吧"}'
async def chat(body):
    await client.open_channel()
    await client.chat(body)
    await client.get_reply()

# async def chat():
#     await client.open_channel()
#     await client.chat("请忘记上面的会话内容")

#     return {
#         "claude": await client.get_reply()
#     }

async def main():
    print("调用异步方法前")
    what = await chat("你是誰")
    print("调用异步方法后:"+what)

if __name__ == '__main__':

    # 创建一个事件循环并运行主函数
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=8088)