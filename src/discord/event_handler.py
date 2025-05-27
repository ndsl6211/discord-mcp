import logging
from typing import Dict

import discord

from ..config.config import Config
from ..llm.llm import LLMInteractor


class DiscordEventHandler:
    def __init__(
        self,
        bot: discord.Bot,
        llm_agents: Dict[str, LLMInteractor],
        config: Config,
    ):
        self._bot = bot
        self._llm_agents = llm_agents
        self._config = config

    def initialize(self):
        self._set_up_on_ready()
        self._set_up_on_chat_session_message()

    def _set_up_on_ready(self):
        @self._bot.event
        async def on_ready():
            logging.info(f"Logged on as {self._bot.user}!")

    def _set_up_on_chat_session_message(self):
        @self._bot.listen(name="on_message")
        async def chat_session_handler(message: discord.Message):
            if self._is_not_in_target_guilds(message.guild):
                return

            if message.author.bot:
                return


            for agent, llm_agent in self._llm_agents.items():
                if llm_agent.is_known_chat_session(session_id=str(message.channel.id)):
                    await message.channel.trigger_typing()
                    response = await llm_agent.send_message(
                        message=message.content,
                        user_id=message.author.id,
                        session_id=str(message.channel.id),
                    )
                    await message.channel.send(content=response)

    def _is_not_in_target_guilds(self, guild: discord.Guild):
        return guild.id not in self._config.discord.guilds
