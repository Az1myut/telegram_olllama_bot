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


def get_email_mcp_server() -> MCPServerStdio | None:
    if not settings.email_sender or not settings.email_password:
        return None
    return MCPServerStdio(
        command="mcp-server-email",
        args=[],
        env={
            "SENDER": settings.email_sender,
            "PASSWORD": settings.email_password,
        },
    )