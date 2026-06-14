from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from handlers.transactions import format_money
from services.transaction_service import TransactionService


router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message, transaction_service: TransactionService):
    stats = await transaction_service.monthly_stats(message.from_user.id)
    text = (
        f"📊 <b>{date.today():%B %Y}</b>\n\n"
        f"💰 Income:  {format_money(stats['income'])}\n"
        f"💸 Expense: {format_money(stats['expense'])}\n"
        f"━━━━━━━━━━\n"
        f"🧮 Net:     {format_money(stats['net'])}"
    )
    await message.answer(text)


@router.message(Command("monthly"))
async def cmd_monthly(message: Message, transaction_service: TransactionService):
    rows = await transaction_service.monthly_comparison(message.from_user.id)
    if not rows:
        await message.answer("Not enough data for a monthly comparison yet.")
        return

    lines = ["📈 <b>Last 3 months</b>\n"]
    for row in rows:
        net = row["income"] - row["expense"]
        lines.append(
            f"<b>{row['month']}</b>\n"
            f"  💰 {format_money(row['income'])}  "
            f"💸 {format_money(row['expense'])}  "
            f"🧮 {format_money(net)}"
        )
    await message.answer("\n".join(lines))
