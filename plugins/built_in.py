from config import conf
from common.singleton import singleton
from common.session import Session
from common.reply import Reply, ReplyType
from plugins.event import Event
from utils.query_key import QueryKey


@singleton
class Cmd:
    def __init__(self, plugins: dict):
        self.config = conf()
        self.plugins = plugins

    def will_generate_reply(self, event: Event):
        query = event.context.query
        session_id = event.context.session_id
        if query == self.config.get("clear_current_session_command", "#clear session"):
            Session.clear_session(session_id)
            event.reply = Reply(ReplyType.TEXT, "The session has been cleared")
            event.bypass()
        elif query == self.config.get(
            "clear_all_sessions_command", "#clear all sessions"
        ):
            Session.clear_all_session()
            event.reply = Reply(ReplyType.TEXT, "All sessions have been cleared")
            event.bypass()
        elif query == self.config.get("query_key_command", "#query key"):
            event.reply = Reply(ReplyType.TEXT, QueryKey.get_key())
            event.bypass()
        elif query.startswith("#help "):
            plugin_name = query.split(" ")[1]
            reply_text = f"No plugin named {plugin_name}"
            for name in self.plugins:
                if name == plugin_name:
                    reply_text = self.plugins[name].help()
                    break
            event.reply = Reply(ReplyType.TEXT, reply_text)
            event.bypass()
