from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from agent import run_agent, clear_history

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
        "make a Notion page about quantum computing trends\n\n"
        "Commands:\n"
        "/clear - Reset conversation history",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "How to use this bot:\n\n"
        "GitHub workflow:\n"
        "find bugs in https://github.com/you/myrepo and open a pull request\n\n"
        "Notion workflow:\n"
        "create a Notion page about the history of the internet\n\n"
        "Commands:\n"
        "/clear - Reset conversation history\n\n"
        "The bot remembers your conversation so you can follow up.",
    )


@router.message(Command("clear"))
async def cmd_clear(message: Message) -> None:
    clear_history(message.chat.id)
    await message.answer("🗑️ Conversation history cleared.")


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
        response = await run_agent(message.text, chat_id=message.chat.id)
        # Split long responses for Telegram's 4096 char limit
        if len(response) <= 4096:
            await status_msg.edit_text(response)
        else:
            await status_msg.delete()
            for i in range(0, len(response), 4096):
                await message.answer(response[i:i + 4096])
    except Exception as e:
        await status_msg.edit_text(
            f"Something went wrong. Please try again.\n\nHint: {type(e).__name__}"
        )