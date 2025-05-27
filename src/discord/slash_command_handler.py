import logging
from typing import Dict

import discord

from ..config.config import Config
from ..llm.llm import LLMInteractor


class DiscordSlashCommandHandler:
    def __init__(
        self,
        bot: discord.Bot,
        llm_agents: Dict[str, LLMInteractor],
        config: Config,
    ):
        self._bot = bot
        self._llm_agents = llm_agents
        self._config = config

        self._chat_command_group = bot.create_group(name="chat")

    def initialize(self):
        self._register_chat_command()

    def _register_chat_command(self):
        # @self._bot.slash_command(
            # name="chat",
            # description="start a chat session",
            # guild_ids=self._config.discord.guilds,
        # )
        @self._chat_command_group.command(
            name="openai",
            description="start a chat session with openai model",
            guild_ids=self._config.discord.guilds,
        )
        async def openai_chat(ctx: discord.ApplicationContext):
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

            openai_agent = self._llm_agents.get("openai")
            if openai_agent is None:
                logging.error("OpenAI agent not found")
                return

            openai_agent.start_new_chat_session(session_id=str(thread.id))
            await thread.send(
                content="Chat session started! You can now send messages."
            )

        @self._chat_command_group.command(
            name="gemini",
            description="start a chat session with gemini model",
            guild_ids=self._config.discord.guilds,
        )
        async def gemini_chat(ctx: discord.ApplicationContext):
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

            gemini_agent = self._llm_agents.get("gemini")
            if gemini_agent is None:
                logging.error("Gemini agent not found")
                return

            gemini_agent.start_new_chat_session(session_id=str(thread.id))
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
