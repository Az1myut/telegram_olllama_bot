from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from agent import run_agent

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Hi! I'm your AI assistant.\n\n"
        "I can help you with:\n"
        "- GitHub: find bugs, fix code, create a pull request\n"
        "- Notion: create a page about any topic\n\n"
        "Just describe what you want. Examples:\n"
        "find bugs in https://github.com/you/repo and make a PR\n"
        "make a Notion page about quantum computing trends",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "How to use this bot:\n\n"
        "GitHub workflow:\n"
        "find bugs in https://github.com/you/myrepo and open a pull request\n\n"
        "Notion workflow:\n"
        "create a Notion page about the history of the internet\n\n"
        "The bot handles everything autonomously.",
    )


@router.message()
async def handle_message(message: Message) -> None:
    if not message.text:
        await message.answer("Please send a text message.")
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing",
    )

    status_msg = await message.answer("Working on it...")

    try:
        response = await run_agent(message.text)
        # Send as plain text — no Markdown parsing to avoid format errors
        await status_msg.edit_text(response)
    except Exception as e:
        await status_msg.edit_text(
            f"Something went wrong:\n{str(e)}\n\nPlease try again."
        )