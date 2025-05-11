from dataclasses import replace
from agents import Agent, Runner
import discord
import logging

from ..repository.chat_session import ChatSession, ChatSessionStorage, Record
from ..config import Config


class DiscordBot:
    def __init__(
        self,
        token: str,
        agent: Agent,
        config: Config,
        chat_session_storage: ChatSessionStorage,
    ):
        self._token = token
        self._agent = agent
        self._config = config
        self._chat_session_storage = chat_session_storage

        self._initialize_bot()
        self._set_up_message_handlers()
        self._set_up_slash_command_handlers()

    def _initialize_bot(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self._bot = discord.Bot(None, intents=intents)

    def _set_up_message_handlers(self):
        @self._bot.event
        async def on_ready():
            logging.info(f"Logged on as {self._bot.user}!")

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
            self._chat_session_storage.add_message(
                session_id=chat_session.id,
                record=record,
            )

            # handle message from the bot
            await message.channel.trigger_typing()

            res = await self._send_message_with_history_to_agent(
                chat_session=chat_session,
                record=record,
            )

            self._chat_session_storage.add_message(
                session_id=chat_session.id,
                record=Record(
                    user_id="bot", role="assistant", message=res.final_output
                ),
            )

            await message.channel.send(content=res.final_output)

    def _set_up_slash_command_handlers(self):
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
            await Runner.run(
                starting_agent=self._agent,
                input=self._config.openai.system_prompt,
                context=chat_session,
            )
            await thread.send(
                content="Chat session started! You can now send messages."
            )

    async def start(self):
        await self._bot.start(self._token)

    async def stop(self):
        await self._bot.close()
        logging.info("Discord bot stopped.")

    async def _send_message_with_history_to_agent(
        self,
        chat_session: ChatSession,
        record: Record,
    ):
        new_chat_session = replace(
            chat_session,
            history=chat_session.history + [record],
        )
        return await Runner.run(
            starting_agent=self._agent,
            input=new_chat_session.get_history(),
        )

    def _is_thread_channel(self, channel: discord.abc.GuildChannel):
        return (
            channel.type == discord.ChannelType.public_thread
            or channel.type == discord.ChannelType.private_thread
            or channel.type == discord.ChannelType.news_thread
        )

    def _is_not_in_target_guilds(self, guild: discord.Guild):
        return guild.id not in self._config.discord.guilds


if __name__ == "__main__":
    pass
