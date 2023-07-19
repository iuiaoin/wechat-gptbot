from common.context import Context
from config import conf
from common.singleton import singleton
from common.reply import Reply


@singleton
class Bot:
    def reply(self, context: Context) -> Reply:
        use_azure_chatgpt = conf().get("use_azure_chatgpt", False)
        if use_azure_chatgpt:
            from bot.azure_chatgpt import AzureChatGPTBot

            return AzureChatGPTBot().reply(context)
        else:
            from bot.chatgpt import ChatGPTBot

            return ChatGPTBot().reply(context)
