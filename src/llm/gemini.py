import os
from typing import override

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..config.config import Config, load_config
from ..llm.llm import LLMInteractor
from ..llm.mcp_server import MCPServerManager


class GeminiAgent(LLMInteractor):
    def __init__(
        self, config: Config, mcp_server_manager: MCPServerManager | None
    ) -> None:
        self._config = config
        self._mcp_server_manager = mcp_server_manager
        self._chat_session_storage = InMemorySessionService()

        self._DEFAULT_APP_NAME = "discord-gemini"
        self._DEFAULT_USER_ID = "bot"

        self._initialize()

    def _initialize(self):
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
        os.environ["GOOGLE_API_KEY"] = self._config.llm.gemini.api_key

        self._agent = Agent(
            name=self._config.llm.agent_name,
            model=self._config.llm.gemini.model,
            instruction=self._config.llm.system_prompt,
            tools=[],
        )

    @override
    def start_new_chat_session(self, session_id: str) -> None:
        self._chat_session_storage.create_session(
            app_name=self._DEFAULT_APP_NAME,
            user_id=self._DEFAULT_USER_ID,
            session_id=session_id,
        )

    @override
    async def send_message(self, message: str, user_id: str, session_id: str) -> str:
        chat_session = self._chat_session_storage.get_session(
            app_name=self._DEFAULT_APP_NAME,
            user_id=self._DEFAULT_USER_ID,
            session_id=str(session_id),
        )
        if chat_session is None:
            raise ValueError(f"Unknown session ID: {session_id}")

        runner = Runner(
            app_name=self._DEFAULT_APP_NAME,
            agent=self._agent,
            session_service=self._chat_session_storage,
        )

        content = types.Content(role="user", parts=[types.Part(text=message)])

        final_response_text = "Sorry, I cannot respond at the moment."
        for event in runner.run(
            user_id=self._DEFAULT_USER_ID,
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break

        return final_response_text


    @override
    def is_known_chat_session(self, session_id: str) -> bool:
        return self._chat_session_storage.get_session(
            app_name=self._DEFAULT_APP_NAME,
            user_id=self._DEFAULT_USER_ID,
            session_id=session_id,
        ) is not None

    @override
    def get_name(self) -> str:
        return "gemini"


if __name__ == "__main__":
    config = load_config()

    gemini = GeminiAgent(config=config, mcp_server_manager=None)
