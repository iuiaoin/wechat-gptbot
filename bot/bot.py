import litellm
from common.context import Context
from config import conf
from common.singleton import singleton
from common.reply import Reply


@singleton
class Bot:
    def __init__(self):
        use_azure_chatgpt = conf().get("use_azure_chatgpt", False)
        model = conf().get("model", "gpt-3.5-turbo")
        if use_azure_chatgpt:
            from bot.azure_chatgpt import AzureChatGPTBot

            self.bot = AzureChatGPTBot()

        elif model in litellm.open_ai_chat_completion_models:
            from bot.chatgpt import ChatGPTBot

            self.bot = ChatGPTBot()
        else:
            # see litellm supported models here:
            # https://litellm.readthedocs.io/en/latest/supported/
            from bot.litellm import LiteLLMChatGPTBot

            self.bot = LiteLLMChatGPTBot()

    def reply(self, context: Context) -> Reply:
        return self.bot.reply(context)
