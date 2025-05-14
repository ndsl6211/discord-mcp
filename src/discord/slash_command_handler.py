import logging

import discord

from ..config.config import Config
from ..llm.llm import LLMInteractor
from ..repository.chat_session import ChatSessionStorage


class DiscordSlashCommandHandler:
    def __init__(
        self,
        bot,
        llm_agent: LLMInteractor,
        config: Config,
        chat_session_storage: ChatSessionStorage,
    ):
        self._bot = bot
        self._llm_agent = llm_agent
        self._config = config
        self._chat_session_storage = chat_session_storage

    def initialize(self):
        self._register_chat_command()

    def _register_chat_command(self):
        @self._bot.slash_command(
            name="chat",
            description="start a chat session",
            guild_ids=self._config.discord.guilds,
        )
        async def chat(ctx: discord.ApplicationContext):
            if self._is_not_in_target_guilds(ctx.guild):
                return

            if self._is_thread_channel(ctx.channel):
                logging.warning("command cannot be used in a thread channel")
                return

            res = await ctx.interaction.respond("Creating a chat session...")

            original_res = await res.original_response()
            thread = await original_res.create_thread(
                name="Chat session",
                auto_archive_duration=60,
            )

            # create a new session
            chat_session = self._chat_session_storage.create_session(
                thread.id,
                system_prompt=self._config.openai.system_prompt,
            )
            # sent the system prompt to the LLM
            await self._llm_agent.send_message(chat_session=chat_session)
            await thread.send(
                content="Chat session started! You can now send messages."
            )

    def _is_thread_channel(self, channel: discord.abc.GuildChannel):
        return (
            channel.type == discord.ChannelType.public_thread
            or channel.type == discord.ChannelType.private_thread
            or channel.type == discord.ChannelType.news_thread
        )

    def _is_not_in_target_guilds(self, guild: discord.Guild):
        return guild.id not in self._config.discord.guilds
