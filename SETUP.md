# Setup Instructions

## Prerequisites

| Tool   | Version | Install                                                                                          |
| ------ | ------- | ------------------------------------------------------------------------------------------------ |
| Python | 3.12+   | [python.org](https://www.python.org/downloads/)                                                  |
| uv     | latest  | `pip install uv` or [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |

---

## 1. Clone / download the project

```bash
git clone <repo-url>
cd simple-mcp
```

---

## 2. Create the virtual environment and install dependencies

```bash
uv sync
```

`uv sync` reads `pyproject.toml`, creates `.venv/` automatically, and installs all dependencies.

### or

```bash
python -m venv .venv

venv\Scripts\activate

pip install .
```

---

## 3. Configure environment variables (optional)

Copy the example file and edit it:

```bash
cp .env.example .env
```

```ini
# .env
HOST=127.0.0.1
PORT=8000
```

The server defaults to `127.0.0.1:8000` if no `.env` is present.

---

## 4. Run the server

```bash
uv run server.py
```

The MCP endpoint will be available at:

```
http://127.0.0.1:8000/mcp
```

---

## 5. Connect an MCP client

Stay tuned to see this...
Make sure you have NGROK installed in your system.
