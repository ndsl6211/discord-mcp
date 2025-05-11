import logging
from typing import Dict

from src.repository.chat_session import ChatSession, ChatSessionStorage, Record


class MemChatSessionStorage(ChatSessionStorage):
    def __init__(self):
        self.chat_sessions: Dict[int, ChatSession] = {}

    def create_session(self, session_id: int) -> ChatSession:
        if session_id in self.chat_sessions:
            logging.warning(f"Session with ID {session_id} already exists. Ignoring.")
            return self.chat_sessions.get(session_id)

        new_session = ChatSession(id=session_id, history=[])
        self.chat_sessions[session_id] = new_session
        return new_session

    def add_message(self, session_id: int, record: Record) -> None:
        if session_id not in self.chat_sessions:
            logging.error(
                f"Session with ID {session_id} does not exist. Cannot add message."
            )
            return

        self.chat_sessions[session_id].history.append(record)

    def get_session(self, session_id: int) -> ChatSession | None:
        if session_id not in self.chat_sessions:
            logging.warning(f"Session with ID {session_id} does not exist.")
            return None

        return self.chat_sessions.get(session_id)

    def get_all_sessions(self) -> Dict[int, ChatSession]:
        return self.chat_sessions
