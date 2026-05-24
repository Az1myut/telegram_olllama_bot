from pydantic_ai.mcp import MCPServerStdio
from config import settings


def get_github_mcp_server() -> MCPServerStdio | None:
    if not settings.github_personal_access_token:
        return None
    return MCPServerStdio(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": settings.github_personal_access_token},
    )


def get_gmail_mcp_server() -> MCPServerStdio | None:
    """Google Workspace MCP server for Gmail (send, read, search emails)."""
    if not settings.google_oauth_client_id or not settings.google_oauth_client_secret:
        return None
    return MCPServerStdio(
        command="uvx",
        args=["workspace-mcp", "--tools", "gmail"],
        env={
            "GOOGLE_OAUTH_CLIENT_ID": settings.google_oauth_client_id,
            "GOOGLE_OAUTH_CLIENT_SECRET": settings.google_oauth_client_secret,
        },
    )