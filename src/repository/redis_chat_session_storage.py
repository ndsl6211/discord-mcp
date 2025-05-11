import json
import logging
from typing import Dict, List
import redis
from src.config.config import RedisConfig
from src.repository.chat_session import ChatSession, ChatSessionStorage, Record


class RedisChatSessionStorage(ChatSessionStorage):
    def __init__(self, redis_config: RedisConfig):
        self._key_prefix = "chat_session:"
        self._client = redis.Redis(
            host=redis_config.host,
            port=redis_config.port,
            password=redis_config.password,
            db=redis_config.db,
        )

    def create_session(self, session_id: int, system_prompt: str | None) -> ChatSession:
        key = f"{self._key_prefix}{session_id}"
        if self._client.exists(key):
            history = self._get_full_message_history(key)
            return ChatSession(id=session_id, history=history)

        initial_record = Record(
            user_id="developer",
            role="developer",
            message="(this is the very beginging of the chat history)",
        )
        self._client.lpush(key, initial_record.to_json())

        if system_prompt:
            system_prompt_record = Record(
                user_id="developer",
                role="system",
                message=system_prompt,
            )
            self._client.lpush(key, system_prompt_record.to_json())

        new_session = ChatSession(
            id=session_id,
            history=[initial_record, system_prompt_record],
        )
        return new_session

    def add_message(self, session_id: int, record: Record) -> None:
        key = f"{self._key_prefix}{session_id}"
        if not self._client.exists(key):
            logging.error(
                f"Session with ID {session_id} does not exist. Cannot add message."
            )
            return

        self._client.lpush(
            key,
            Record(
                user_id=record.user_id,
                role=record.role,
                message=record.message,
            ).to_json(),
        )

    def get_session(self, session_id: int) -> ChatSession | None:
        key = f"{self._key_prefix}{session_id}"
        if not self._client.exists(key):
            logging.warning(f"Session with ID {session_id} does not exist.")
            return None

        history = self._get_full_message_history(key)
        return ChatSession(id=session_id, history=history)

    def get_all_sessions(self) -> Dict[int, ChatSession]:
        logging.warning("not implemented yet")

    def _get_full_message_history(self, key) -> List[Record]:
        session_data = self._client.lrange(key, 0, -1)

        return [
            Record(
                user_id=record["user_id"],
                role=record["role"],
                message=record["message"],
            )
            for record in [json.loads(data) for data in session_data]
        ]
