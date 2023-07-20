import openai
from bot.chatgpt import ChatGPTBot
from config import conf


class AzureChatGPTBot(ChatGPTBot):
    def __init__(self):
        super().__init__()
        openai.api_type = "azure"
        openai.api_version = "2023-06-01-preview"
        self.args["deployment_id"] = conf().get("azure_deployment_id")
