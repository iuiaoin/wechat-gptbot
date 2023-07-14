from common.expired_dict import ExpiredDict
from config import conf
from common.context import Context


class Session(object):
    all_sessions = ExpiredDict(conf().get("session_expired_duration") or 3600)

    @staticmethod
    def build_session_query(context: Context):
        """
        build query with conversation history
        e.g.  [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
        :param query: query content
        :param session_id: session id
        :return: query content with conversaction
        """
        session = Session.all_sessions.get(context.session_id, [])
        if len(session) == 0:
            system_item = {"role": "system", "content": context.system_prompt}
            session.append(system_item)
            Session.all_sessions[context.session_id] = session
        user_item = {"role": "user", "content": context.query}
        session.append(user_item)
        return session

    @staticmethod
    def save_session(answer, session_id, total_tokens):
        max_tokens = conf().get("max_tokens")
        session = Session.all_sessions.get(session_id)
        if session:
            # append conversation
            gpt_item = {"role": "assistant", "content": answer}
            session.append(gpt_item)

        # discard exceed limit conversation
        Session.discard_exceed_conversation(session, max_tokens, total_tokens)

    @staticmethod
    def discard_exceed_conversation(session, max_tokens, total_tokens):
        dec_tokens = int(total_tokens)
        while dec_tokens > max_tokens:
            # pop first conversation
            if len(session) > 3:
                session.pop(1)
                session.pop(1)
            else:
                break
            dec_tokens = dec_tokens - max_tokens

    @staticmethod
    def clear_session(session_id):
        Session.all_sessions[session_id] = []

    @staticmethod
    def clear_all_session():
        Session.all_sessions.clear()
