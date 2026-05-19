from __future__ import annotations

import logging

from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

from config import settings
from mcp_servers import get_github_mcp_server, get_zapier_mcp_server
from tools.web_fetch import fetch_web_page, web_search_via_ddg

logger = logging.getLogger(__name__)

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
6. Use the Zapier Send Email tool to notify the user that a PR was opened.
7. Reply to the user with the PR link.

## Workflow 2 - Notion Page Creation
When the user asks you to create a Notion page about a topic:
1. If you need current information, use the web_search_via_ddg tool first.
2. If you need to read a specific URL, use the fetch_web_page tool.
3. Compose well-structured content from what you know plus what you fetched.
4. Use the Zapier Create Notion Page tool to create the page.
5. Reply to the user with the Notion page URL.

## General rules
- For simple greetings or questions, just reply normally without using any tools.
- Only use tools when the task clearly requires them.
- Be concise in replies.
- Each message is independent, do not assume previous context.
"""


def build_ollama_model() -> OllamaModel:
    provider = OllamaProvider(base_url=settings.ollama_base_url)
    return OllamaModel(
        model_name=settings.ollama_model,
        provider=provider,
    )


def build_agent() -> Agent:
    model = build_ollama_model()

    toolsets = []
    github = get_github_mcp_server()
    zapier = get_zapier_mcp_server()
    if github:
        toolsets.append(github)
    if zapier:
        toolsets.append(zapier)

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        toolsets=toolsets if toolsets else None,
    )

    agent.tool_plain(web_search_via_ddg)
    agent.tool_plain(fetch_web_page)

    return agent


async def run_agent(user_message: str) -> str:
    logger.info("Running agent for message: %s", user_message)
    agent = build_agent()

    try:
        if agent.toolsets:
            # Only open MCP context if there are MCP servers configured
            async with agent:
                result = await agent.run(user_message)
        else:
            result = await agent.run(user_message)

        logger.info("Agent result: %s", result.output)
        return result.output

    except Exception as e:
        logger.error("Agent error: %s", e, exc_info=True)
        raise