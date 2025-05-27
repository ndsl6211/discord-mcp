import base64
import logging
import os
from typing import override

import logfire
import nest_asyncio
from agents import Agent, Runner, set_default_openai_key
from openai.types.responses import EasyInputMessageParam

from ..config.config import Config
from ..llm.llm import LLMInteractor
from ..llm.mcp_server import MCPServerManager
from ..repository.chat_session import ChatSessionStorage, Record


class OpenAiAgent(LLMInteractor):
    def __init__(
        self,
        config: Config,
        mcp_server_manager: MCPServerManager,
        chat_session_storage: ChatSessionStorage,
    ) -> None:
        self._config = config
        self._mcp_server_manager = mcp_server_manager
        self._chat_session_storage = chat_session_storage

        self._set_up_langfuse()
        self._initialize()

    def _set_up_langfuse(self):
        os.environ["LANGFUSE_SECRET_KEY"] = self._config.llm.openai.tracing.langfuse.secret_key
        os.environ["LANGFUSE_PUBLIC_KEY"] = self._config.llm.openai.tracing.langfuse.public_key
        os.environ["LANGFUSE_HOST"] = self._config.llm.openai.tracing.langfuse.host
        LANGFUSE_AUTH = base64.b64encode(
            f"{os.environ.get('LANGFUSE_PUBLIC_KEY')}:{os.environ.get('LANGFUSE_SECRET_KEY')}".encode()
        ).decode()
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = (
            os.environ.get("LANGFUSE_HOST") + "/api/public/otel"
        )
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = (
            f"Authorization=Basic {LANGFUSE_AUTH}"
        )
        os.environ["OPENAI_API_KEY"] = self._config.llm.openai.api_key

        nest_asyncio.apply()

        logfire.configure(
            service_name="my_agent_service",
            send_to_logfire=False,
        )
        logfire.instrument_openai_agents()

    def _initialize(self):
        set_default_openai_key(self._config.llm.openai.api_key)
        self._agent = Agent(
            name=self._config.llm.agent_name,
            instructions=self._config.llm.system_prompt,
            model=self._config.llm.openai.model,
            mcp_servers=[s for s in self._mcp_server_manager.get()],
        )

    @override
    def start_new_chat_session(self, session_id: str) -> None:
        self._chat_session_storage.create_session(
            session_id=session_id,
            system_prompt=self._config.llm.system_prompt,
        )

    @override
    async def send_message(self, message: str, user_id: str, session_id: str) -> str:
        chat_session = self._chat_session_storage.get_session(session_id)
        if chat_session is None:
            raise ValueError(f"Unknown session ID: {session_id}")

        chat_session = self._chat_session_storage.add_message(
            session_id=chat_session.id,
            record=Record(
                user_id=user_id,
                role="user",
                message=message,
            ),
        )

        res = await Runner.run(
            starting_agent=self._agent,
            input=[
                EasyInputMessageParam(
                    content=r.message,
                    role=r.role,
                    type="message",
                )
                for r in chat_session.history
            ],
        )

        if res.final_output is None:
            logging.warning("No final output from OpenAI agent")
            return None

        self._chat_session_storage.add_message(
            session_id=chat_session.id,
            record=Record(
                user_id="bot",
                role="assistant",
                message=res.final_output,
            ),
        )

        return res.final_output

    @override
    def is_known_chat_session(self, session_id: str) -> bool:
        return self._chat_session_storage.get_session(session_id) is not None

    @override
    def get_name(self) -> str:
        return "openai"
