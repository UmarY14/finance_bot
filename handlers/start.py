import html

from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.user_service import UserService


router = Router()

HELP = (
    "<b>Finance Tracker</b>\n"
    "/add — add a transaction\n"
    "/stats — this month's income/expense/net\n"
    "/history — last 10 transactions\n"
    "/categories — manage categories\n"
    "/report — export this month to CSV\n"
    "/limit — set a monthly category limit\n"
    "/monthly — last 3 months comparison\n"
    "/cancel — cancel the current action"
)


@router.message(CommandStart())
async def cmd_start(message: Message, user_service: UserService):
    name = message.from_user.full_name
    safe_name = html.escape(name)
    created = await user_service.register(message.from_user.id, name)
    if created:
        await message.answer(f"👋 Welcome, {safe_name}! You're registered.\n\n" + HELP)
    else:
        await message.answer(f"✅ You're already registered, {safe_name}.\n\n" + HELP)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP)


@router.message(Command("cancel"), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext):
    if await state.get_state() is None:
        await message.answer("Nothing to cancel.")
        return

    await state.clear()
    await message.answer("❌ Cancelled.")
