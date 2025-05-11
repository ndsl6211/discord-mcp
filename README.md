# discord-mcp

A mcp-pluggable Discord bot designed to interact with OpenAI models.

## Prerequisites

### Discord bot

Please go to [Discord Developer Portal](https://discord.com/developers/applications) and create a
new application. Then, create a bot user for the application. Make sure to copy the bot token, as
you will need it later.

### Tracing

This project uses Langfuse to monitor OpenAI's model usage. Please create your API credentials on
[Langfuse](https://langfuse.com/). Or you can run your own instance of Langfuse by using the
docker-compose.yaml file.

### OpenAI API key

Please create an OpenAI account and get your API key from the [OpenAI
API](https://platform.openai.com/account/api-keys).

### Configure you MCP servers

You can install whatever MCP server you want when you run the bot. Please create a `mcp.json` file
in the root directory of this project with the following format:

```json
{
  "servers": {
    "you-mcp-server-1": {
      "command": "",
      "args": [],
      "env": {}
    },
    "you-mcp-server-2": {
      "command": "",
      "args": [],
      "env": {}
    }
  }
}
```

## Run the bot

1. Install the dependencies:

```bash
uv sync
```

2. Create a `config.yaml` file in the root directory of this project, and fill it with all the
   required values. You can refer to the `config.example.yaml`.

3. Run the bot:

run the bot in your terminal:

```bash
uv run -m src.main
```

or run it as a Docker container:

```bash
docker build -t discord-mcp .

docker run -it --rm --name discord-mcp discord-mcp
```

