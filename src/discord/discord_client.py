import logging

import discord

from ..config import Config
from ..llm.llm import LLMInteractor
from ..repository.chat_session import ChatSessionStorage
from .event_handler import DiscordEventHandler
from .slash_command_handler import DiscordSlashCommandHandler


class DiscordBot:
    def __init__(
        self,
        token: str,
        llm_agent: LLMInteractor,
        config: Config,
        chat_session_storage: ChatSessionStorage,
    ):
        self._token = token
        self._config = config
        self._chat_session_storage = chat_session_storage

        self._initialize_bot()

        self._event_handler = DiscordEventHandler(
            bot=self._bot,
            llm_agent=llm_agent,
            config=config,
            chat_session_storage=chat_session_storage,
        )
        self._event_handler.initialize()
        self._slash_command_handler = DiscordSlashCommandHandler(
            self._bot,
            llm_agent=llm_agent,
            config=config,
            chat_session_storage=chat_session_storage,
        )
        self._slash_command_handler.initialize()

    def _initialize_bot(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self._bot = discord.Bot(None, intents=intents)

    async def start(self):
        await self._bot.start(self._token)

    async def stop(self):
        await self._bot.close()
        logging.info("Discord bot stopped.")


if __name__ == "__main__":
    pass
