import openai
import requests
from bot.chatgpt import ChatGPTBot
from common.singleton import singleton
from config import conf
from utils.log import logger
from common.reply import Reply, ReplyType


@singleton
class AzureChatGPTBot(ChatGPTBot):
    def __init__(self):
        super().__init__()
        openai.api_type = "azure"
        openai.api_version = "2023-03-15-preview"
        self.args["deployment_id"] = conf().get("azure_deployment_id")

    def reply_img(self, query):
        create_image_size = conf().get("create_image_size", "256x256")
        try:
            response = openai.Image.create(prompt=query, n=1, size=create_image_size)
            image_url = response["data"][0]["url"]
            logger.info(f"[ChatGPT] Image={image_url}")
            return Reply(ReplyType.IMAGE, image_url)
        except Exception as e:
            logger.error(f"[ChatGPT] Create image failed: {e}")
            return Reply(ReplyType.TEXT, "Image created failed")

    def create_img(self, query):
        url = f"{openai.api_base}dalle/text-to-image?api-version=2022-08-03-preview"
        headers = {"api-key": openai.api_key, "Content-Type": "application/json"}
        create_image_size = conf().get("create_image_size", "256x256")
        try:
            body = {"caption": query, "resolution": create_image_size}
            submission = requests.post(url, headers=headers, json=body)
            operation_location = submission.headers["Operation-Location"]
            response = requests.get(operation_location, headers=headers)
            image_url = response.json()["result"]["contentUrl"]
            logger.info(f"[ChatGPT] Image={image_url}")
            return Reply(ReplyType.IMAGE, image_url)
        except Exception as e:
            logger.error(f"[ChatGPT] Create image failed: {e}")
            return Reply(ReplyType.TEXT, "Image created failed")
