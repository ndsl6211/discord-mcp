import logging

import discord

from ..config.config import Config
from ..llm.llm import LLMInteractor
from ..repository.chat_session import ChatSessionStorage, Record


class DiscordEventHandler:
    def __init__(
        self,
        bot: discord.Bot,
        llm_agent: LLMInteractor,
        config: Config,
        chat_session_storage: ChatSessionStorage,
    ):
        self._bot = bot
        self._llm_agent = llm_agent
        self._config = config
        self._chat_session_storage = chat_session_storage

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

            # handle message from the user
            chat_session = self._chat_session_storage.get_session(message.channel.id)
            if chat_session is None:
                logging.warning("unknown chat session, ignoring message")
                return

            record = Record(
                user_id=message.author.id,
                role="user",
                message=message.content,
            )
            chat_session = self._chat_session_storage.add_message(
                session_id=chat_session.id,
                record=record,
            )

            # handle message from the bot
            await message.channel.trigger_typing()

            response = await self._llm_agent.send_message(chat_session=chat_session)

            self._chat_session_storage.add_message(
                session_id=chat_session.id,
                record=Record(
                    user_id="bot",
                    role="assistant",
                    message=response,
                ),
            )

            await message.channel.send(content=response)

    def _is_not_in_target_guilds(self, guild: discord.Guild):
        return guild.id not in self._config.discord.guilds
