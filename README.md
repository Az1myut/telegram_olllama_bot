# 🤖 Telegram AI Bot

A Python Telegram bot powered by **PydanticAI** + **Ollama (llama3.1:8b)** that can:
- 🐛 Find bugs in GitHub repos, fix them, open a PR, and email you the link
- 📄 Create Notion pages about any topic (with automatic web search)

---

## Stack

| Component | Technology |
|---|---|
| Telegram interface | aiogram 3.x |
| AI orchestration | PydanticAI |
| Local LLM | Ollama llama3.1:8b |
| GitHub tools | GitHub MCP server (npx) |
| Email + Notion | Zapier MCP (HTTP) |
| Web search | DuckDuckGo (no API key) |

---

## Prerequisites

- Python 3.11+
- Node.js 18+ (for GitHub MCP server via npx)
- [Ollama](https://ollama.com) installed and running locally

---

## Setup

### 1. Pull the Ollama model
```bash
ollama pull llama3.1:8b
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
# Also install pydantic-settings (needed for config.py)
pip install pydantic-settings
```

### 3. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` and fill in:

| Variable | Where to get it |
|---|---|
| `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) on Telegram |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub → Settings → Developer settings → Personal access tokens → **repo** scope |
| `GITHUB_USERNAME` | Your GitHub username |
| `ZAPIER_MCP_URL` | See Zapier setup below |

### 4. Set up Zapier MCP

1. Go to [https://actions.zapier.com/mcp](https://actions.zapier.com/mcp)
2. Enable the MCP server
3. Add two actions:
   - **Gmail / SMTP → Send Email**
   - **Notion → Create Page**
4. Copy the MCP URL into your `.env` as `ZAPIER_MCP_URL`

### 5. Run the bot
```bash
python main.py
```

---

## Usage Examples

Send these messages to your bot on Telegram:

**GitHub use case:**
```
find bugs in https://github.com/yourusername/myrepo and make a pull request
```

**Notion use case:**
```
create a Notion page about the latest trends in renewable energy
```

---

## Project Structure

```
.
├── main.py              # Bot entry point
├── agent.py             # PydanticAI agent + tool registration
├── mcp_servers.py       # GitHub MCP + Zapier MCP config
├── config.py            # Settings loaded from .env
├── handlers/
│   └── chat.py          # aiogram message handlers
├── tools/
│   └── web_fetch.py     # Web search + page fetch tools
├── requirements.txt
└── .env.example
```

---

## Notes & Limitations

- **llama3.1:8b tool calling** works but is less reliable than cloud models for complex multi-step tasks. If you find it struggles, consider upgrading to `llama3.1:70b` (needs more RAM) or routing through an OpenAI-compatible endpoint.
- **Each message is independent** — the bot has no memory between messages. Include all needed context (e.g. the full repo URL) in your prompt.
- **Zapier MCP** requires the Zapier account to have the Notion and Gmail integrations connected and authorized.
- **GitHub MCP** requires Node.js on the same machine as the bot (used via `npx`).

---

## Troubleshooting

**Ollama not responding:**
```bash
ollama serve   # make sure it's running
curl http://localhost:11434/api/tags  # verify
```

**GitHub MCP fails:**
```bash
npx -y @modelcontextprotocol/server-github  # test manually
```

**Bot not responding on Telegram:**
- Check `TELEGRAM_BOT_TOKEN` is correct
- Make sure you started a conversation with the bot first (`/start`)
