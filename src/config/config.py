import json
from dataclasses import dataclass
from typing import Any, Dict, List, Literal

import yaml

from src.llm import llm


@dataclass
class DiscordConfig:
    bot_token: str | None
    guilds: List[str] | None


@dataclass
class RedisConfig:
    host: str | None
    port: int | None
    password: str | None
    db: int | None


@dataclass
class ChatHistoryConfig:
    storage: Literal["mem", "redis"]
    redis: RedisConfig | None


@dataclass
class TracingConfig:
    @dataclass
    class LangfuseConfig:
        secret_key: str | None
        public_key: str | None
        host: str | None

    langfuse: LangfuseConfig


@dataclass
class OpenAIConfig:
    api_key: str | None
    model: str | None
    chat_history: ChatHistoryConfig | None
    tracing: TracingConfig | None


@dataclass
class GeminiConfig:
    api_key: str | None
    model: str | None


@dataclass
class LLMConfig:
    openai: OpenAIConfig | None
    gemini: GeminiConfig | None
    agent_name: str | None
    system_prompt: str | None


@dataclass
class Config:
    discord: DiscordConfig
    llm: LLMConfig


def _load_config_from_yaml(filename: str):
    with open(filename, "r") as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            print(f"Error loading YAML config: {e}")
            return None


def _load_config_from_json(filename: str):
    with open(filename, "r") as f:
        try:
            config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            print(f"Error loading JSON config: {e}")
            return None


def load_config() -> Config:
    config = _load_config_from_yaml("config.yaml")
    if config is None:
        raise ValueError("Failed to load configuration from YAML file.")

    config = Config(
        discord=DiscordConfig(
            bot_token=config.get("discord").get("botToken"),
            guilds=config.get("discord").get("guilds"),
        ),
        llm=LLMConfig(
            openai=OpenAIConfig(
                api_key=config.get("llm").get("openai").get("apiKey"),
                model=config.get("llm").get("openai").get("model"),
                chat_history=ChatHistoryConfig(
                    storage=config.get("llm")
                    .get("openai")
                    .get("chatHistory")
                    .get("storage"),
                    redis=RedisConfig(
                        host=config.get("llm")
                        .get("openai")
                        .get("chatHistory")
                        .get("redisHost"),
                        port=config.get("llm")
                        .get("openai")
                        .get("chatHistory")
                        .get("redisPort"),
                        password=config.get("llm")
                        .get("openai")
                        .get("chatHistory")
                        .get("redisPassword"),
                        db=config.get("llm")
                        .get("openai")
                        .get("chatHistory")
                        .get("redisDb"),
                    )
                    if config.get("llm").get("openai").get("chatHistory").get("storage")
                    == "redis"
                    else None,
                ),
                tracing=TracingConfig(
                    langfuse=TracingConfig.LangfuseConfig(
                        secret_key=config.get("llm")
                        .get("openai")
                        .get("tracing")
                        .get("langfuse")
                        .get("secretKey"),
                        public_key=config.get("llm")
                        .get("openai")
                        .get("tracing")
                        .get("langfuse")
                        .get("publicKey"),
                        host=config.get("llm")
                        .get("openai")
                        .get("tracing")
                        .get("langfuse")
                        .get("host"),
                    ),
                ),
            ),
            gemini=GeminiConfig(
                api_key=config.get("llm").get("gemini").get("apiKey"),
                model=config.get("llm").get("gemini").get("model"),
            ),
            agent_name=config.get("llm").get("agentName"),
            system_prompt=config.get("llm").get("systemPrompt"),
        ),
    )
    return config


def load_mcp_server_config() -> Dict[str, Any]:
    config_filename = "mcp.json"
    mcp_config = _load_config_from_json(config_filename)
    if mcp_config is None:
        raise ValueError(
            f"Failed to load MCP server configuration from {config_filename}."
        )

    return mcp_config
