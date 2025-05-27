import logging
from typing import Dict

import discord

from ..config import Config
from ..llm.llm import LLMInteractor
from .event_handler import DiscordEventHandler
from .slash_command_handler import DiscordSlashCommandHandler


class DiscordBot:
    def __init__(
        self,
        token: str,
        llm_agents: Dict[str, LLMInteractor],
        config: Config,
    ):
        self._token = token
        self._config = config

        self._initialize_bot()

        self._event_handler = DiscordEventHandler(
            bot=self._bot,
            llm_agents=llm_agents,
            config=config,
        )
        self._event_handler.initialize()
        self._slash_command_handler = DiscordSlashCommandHandler(
            self._bot,
            llm_agents=llm_agents,
            config=config,
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
