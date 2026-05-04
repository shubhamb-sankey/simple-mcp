# simple-mcp

A minimal MCP server built with [FastMCP](https://github.com/jlowin/fastmcp) and served over **streamable-http**.

## Tools

| Tool | Input | Description |
|---|---|---|
| `ping` | — | Returns `pong`. Health check. |
| `echo` | `message: str` | Reflects the message back in multiple cases. |
| `calculator` | `operation, a, b` | `add` / `subtract` / `multiply` / `divide` on two numbers. |
| `current_time` | — | Returns local date and time (`YYYY-MM-DD HH:MM:SS`). |
| `current_weather` | `location: str` | Current temperature and wind speed for any city via Open-Meteo. |

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Setup

See [SETUP.md](SETUP.md) for full installation and configuration instructions.

## Quick start

```bash
uv run server.py
```

Server listens on `http://127.0.0.1:8000/mcp` by default.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `HOST` | `127.0.0.1` | Bind address |
| `PORT` | `8000` | Bind port |

Copy `.env.example` to `.env` and edit as needed.
