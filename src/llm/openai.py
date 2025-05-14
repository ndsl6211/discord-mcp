import base64
import os

import logfire
import nest_asyncio
from agents import Agent, Runner, set_default_openai_key
from openai.types.responses import EasyInputMessageParam

from ..config.config import Config
from ..llm.llm import LLMInteractor
from ..llm.mcp_server import MCPServerManager
from ..repository.chat_session import ChatSession


class OpenAiAgent(LLMInteractor):
    def __init__(self, config: Config, mcp_server_manager: MCPServerManager) -> None:
        self._config = config
        self._mcp_server_manager = mcp_server_manager

        self._set_up_langfuse()
        self._initialize()

    def _set_up_langfuse(self):
        os.environ["LANGFUSE_SECRET_KEY"] = self._config.tracing.langfuse.secret_key
        os.environ["LANGFUSE_PUBLIC_KEY"] = self._config.tracing.langfuse.public_key
        os.environ["LANGFUSE_HOST"] = self._config.tracing.langfuse.host
        LANGFUSE_AUTH = base64.b64encode(
            f"{os.environ.get('LANGFUSE_PUBLIC_KEY')}:{os.environ.get('LANGFUSE_SECRET_KEY')}".encode()
        ).decode()
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = (
            os.environ.get("LANGFUSE_HOST") + "/api/public/otel"
        )
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = (
            f"Authorization=Basic {LANGFUSE_AUTH}"
        )
        os.environ["OPENAI_API_KEY"] = self._config.openai.api_key

        nest_asyncio.apply()

        logfire.configure(
            service_name="my_agent_service",
            send_to_logfire=False,
        )
        logfire.instrument_openai_agents()

    def _initialize(self):
        set_default_openai_key(self._config.openai.api_key)
        self._agent = Agent(
            name=self._config.openai.agent_name,
            instructions=self._config.openai.system_prompt,
            model=self._config.openai.model,
            mcp_servers=[s for s in self._mcp_server_manager.get()],
        )

    async def send_message(self, chat_session: ChatSession) -> str:
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

        return res.final_output

    def get_name(self) -> str:
        return "openai"
