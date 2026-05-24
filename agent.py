from __future__ import annotations

import logging
from collections import defaultdict

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

from config import settings
from mcp_servers import get_github_mcp_server, get_gmail_mcp_server
from tools.web_fetch import fetch_web_page, web_search_via_ddg

logger = logging.getLogger(__name__)

# Per-chat conversation history (chat_id -> list of messages)
_chat_histories: dict[int, list[ModelMessage]] = defaultdict(list)

# Max history entries per chat to avoid memory bloat
MAX_HISTORY = 20

SYSTEM_PROMPT = """
You are a helpful assistant connected to a Telegram bot.

You help the user with two main workflows:

## Workflow 1 - GitHub Bug Fix & Pull Request
When the user asks you to find bugs, fix code, or make a pull request in a
GitHub repository:
1. Use the GitHub MCP tools to fetch file contents from the repo.
2. Analyse the code, identify bugs or issues.
3. Create a new branch (name it fix/agent-<short-description>).
4. Commit the fixed files to that branch.
5. Open a pull request from that branch to main with a clear description.
6. Use the Gmail MCP tools (e.g. send_email or gmail_send) to notify the user that a PR was opened.
7. Reply to the user with the PR link.

## Workflow 2 - Notion Page Creation
When the user asks you to create a Notion page about a topic:
1. If you need current information, use the web_search_via_ddg tool first.
2. If you need to read a specific URL, use the fetch_web_page tool.
3. Compose well-structured content from what you know plus what you fetched.
4. Reply to the user with the composed content.

## General rules
- For simple greetings or questions, just reply normally without using any tools.
- Only use tools when the task clearly requires them.
- Be concise in replies.
- IMPORTANT: When a task requires tools, actually USE the tools immediately.
  Do NOT just describe what you would do. Execute the actions step by step.
"""


def build_ollama_model() -> OllamaModel:
    provider = OllamaProvider(
        base_url=settings.ollama_base_url,
        api_key=settings.ollama_api_key or "",
    )
    return OllamaModel(
        model_name=settings.ollama_model,
        provider=provider,
    )


def build_agent() -> Agent:
    model = build_ollama_model()

    toolsets = []
    github = get_github_mcp_server()
    gmail = get_gmail_mcp_server()
    if github:
        toolsets.append(github)
    if gmail:
        toolsets.append(gmail)

    # Include GitHub username in prompt if configured
    prompt = SYSTEM_PROMPT
    if settings.github_username:
        prompt += (
            f"\n\nGitHub configuration:"
            f"\n- Owner/username: {settings.github_username}"
            f"\n- When using get_file_contents, use parameters: owner, repo, path"
            f"\n- Do NOT pass 'branch' parameter — use 'ref' for branch name if needed"
            f"\n- Default branch is 'main'"
        )

    agent = Agent(
        model=model,
        system_prompt=prompt,
        toolsets=toolsets if toolsets else None,
        retries=5,
    )

    agent.tool_plain(web_search_via_ddg)
    agent.tool_plain(fetch_web_page)

    return agent


async def run_agent(user_message: str, chat_id: int = 0) -> str:
    """Run the agent with per-chat conversation history."""
    logger.info("Running agent for chat %s: %s", chat_id, user_message)
    agent = build_agent()

    # Get existing history for this chat
    message_history = _chat_histories[chat_id] if chat_id else None

    try:
        if agent.toolsets:
            try:
                async with agent:
                    result = await agent.run(
                        user_message,
                        message_history=message_history,
                    )
            except Exception as mcp_err:
                if "Connection closed" in str(mcp_err) or "TaskGroup" in str(mcp_err):
                    # MCP server failed to start — retry without MCP toolsets
                    logger.warning("MCP server failed, retrying without MCP: %s", mcp_err)
                    agent_no_mcp = Agent(
                        model=build_ollama_model(),
                        system_prompt=SYSTEM_PROMPT,
                        retries=5,
                    )
                    agent_no_mcp.tool_plain(web_search_via_ddg)
                    agent_no_mcp.tool_plain(fetch_web_page)
                    result = await agent_no_mcp.run(
                        user_message,
                        message_history=message_history,
                    )
                else:
                    raise
        else:
            result = await agent.run(
                user_message,
                message_history=message_history,
            )

        # Save updated history (trim to MAX_HISTORY)
        if chat_id:
            _chat_histories[chat_id] = list(result.all_messages())[-MAX_HISTORY:]

        logger.info("Agent result: %s", result.output)
        return result.output

    except Exception as e:
        logger.error("Agent error: %s", e, exc_info=True)
        error_msg = str(e).lower()
        if "connection" in error_msg or "connect" in error_msg:
            return (
                f"⚠️ Cannot connect to Ollama at {settings.ollama_base_url}\n\n"
                "Please make sure:\n"
                "1. Ollama is installed (https://ollama.ai)\n"
                "2. Ollama is running: `ollama serve`\n"
                f"3. Model is pulled: `ollama pull {settings.ollama_model}`\n"
                "4. OLLAMA_BASE_URL in .env is correct"
            )
        if "not found" in error_msg or "resource not found" in error_msg:
            return (
                "⚠️ GitHub resource not found.\n\n"
                "Please check:\n"
                "- Repository name and owner are correct\n"
                "- The file/path exists in the repo\n"
                "- Your GitHub token has access to the repo"
            )
        raise


def clear_history(chat_id: int) -> None:
    """Clear conversation history for a chat."""
    _chat_histories.pop(chat_id, None)