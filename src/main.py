import asyncio
import logging

from langfuse import Langfuse
from agents import Agent, set_default_openai_key

from src.llm.openai import OpenAiAgent
from src.repository.redis_chat_session_storage import RedisChatSessionStorage
from .repository.mem_chat_session_storage import MemChatSessionStorage
from .config.config import load_config, load_mcp_server_config
from .discord.discord_client import DiscordBot
from .llm.mcp_server import MCPServerManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] (%(name)s) %(message)s",
)


async def main():
    config = load_config()
    mcp_server_config = load_mcp_server_config()

    mem_chat_session_storage = MemChatSessionStorage()
    redis_chat_session_storage = RedisChatSessionStorage(
        config.openai.chat_history.redis
    )

    mcp_server_manager = MCPServerManager(mcp_server_config=mcp_server_config)

    try:
        await mcp_server_manager.start()

        openai_agent = OpenAiAgent(config=config, mcp_server_manager=mcp_server_manager) 

        discord_bot = DiscordBot(
            token=config.discord.bot_token,
            agent=openai_agent.get_agent(),
            config=config,
            chat_session_storage=redis_chat_session_storage,
        )
        await discord_bot.start()
    except asyncio.CancelledError:
        logging.info("Shutting down gracefully...")
        await mcp_server_manager.stop()
        await discord_bot.stop()
        logging.info("All servers closed.")


if __name__ == "__main__":
    asyncio.run(main())
