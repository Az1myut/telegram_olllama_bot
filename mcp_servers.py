from pydantic_ai.mcp import MCPServerStdio, MCPServerSSE
from config import settings


def get_github_mcp_server() -> MCPServerStdio | None:
    if not settings.github_personal_access_token:
        return None
    return MCPServerStdio(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": settings.github_personal_access_token},
    )


def get_zapier_mcp_server() -> MCPServerSSE | None:
    if not settings.zapier_mcp_url:
        return None
    return MCPServerSSE(url=settings.zapier_mcp_url)