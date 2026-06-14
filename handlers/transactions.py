import asyncio
import csv
import html
import logging
import os
import tempfile
from datetime import date
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, FSInputFile, Message

from keyboards.inline import (
    cancel_keyboard,
    category_keyboard,
    skip_note_keyboard,
    type_keyboard,
)
from services.category_service import CategoryService
from services.chart_service import ChartService
from services.transaction_service import TransactionService


router = Router()
logger = logging.getLogger(__name__)


async def send_stats_chart(
    target: Message,
    user_id: int,
    transaction_service: TransactionService,
    chart_service: ChartService,
    caption: str | None = None,
) -> None:
    """Render this month's overview chart and send it. Never raises: a chart
    failure must not break the surrounding command."""
    try:
        stats = await transaction_service.monthly_stats(user_id)
        breakdown = await transaction_service.expense_by_category(user_id)
        month_label = date.today().strftime("%B %Y")
        png = await asyncio.to_thread(
            chart_service.render_monthly_overview,
            month_label,
            stats["income"],
            stats["expense"],
            stats["net"],
            breakdown,
        )
        await target.answer_photo(
            BufferedInputFile(png, filename="stats.png"), caption=caption
        )
    except Exception:
        logger.exception("Failed to render/send stats chart")


# Largest value that fits the amount column NUMERIC(12, 2).
MAX_AMOUNT = Decimal("9999999999.99")


def parse_amount(text: str) -> Decimal | None:
    cleaned = (text or "").strip().lower()
    for junk in (" ", ",", "so'm", "som", "uzs"):
        cleaned = cleaned.replace(junk, "")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return None
    if value <= 0 or value > MAX_AMOUNT:
        return None
    return value


def format_money(value) -> str:
    return f"{Decimal(value):,.2f}"


class AddTransaction(StatesGroup):
    amount = State()
    type = State()
    category = State()
    new_category = State()
    note = State()


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    await state.set_state(AddTransaction.amount)
    await message.answer("💵 Enter the amount:", reply_markup=cancel_keyboard())


@router.message(AddTransaction.amount)
async def add_amount(message: Message, state: FSMContext):
    amount = parse_amount(message.text)
    if amount is None:
        await message.answer(
            "⚠️ Invalid amount. Send a positive number up to 9,999,999,999 "
            "(e.g. 45000):",
            reply_markup=cancel_keyboard(),
        )
        return

    await state.update_data(amount=str(amount))
    await state.set_state(AddTransaction.type)
    await message.answer("Choose type:", reply_markup=type_keyboard())


@router.callback_query(AddTransaction.type, F.data.startswith("add:type:"))
async def add_type(
    callback: CallbackQuery, state: FSMContext, category_service: CategoryService
):
    type_ = callback.data.split(":")[2]
    await state.update_data(type=type_)
    categories = await category_service.list_by_type(callback.from_user.id, type_)
    await state.set_state(AddTransaction.category)
    await callback.message.edit_text(
        "Choose a category:", reply_markup=category_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(AddTransaction.category, F.data.startswith("add:cat:"))
async def add_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category_id=int(callback.data.split(":")[2]))
    await state.set_state(AddTransaction.note)
    await callback.message.edit_text(
        "📝 Send a note, or skip:", reply_markup=skip_note_keyboard()
    )
    await callback.answer()


@router.callback_query(AddTransaction.category, F.data == "add:newcat")
async def add_new_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddTransaction.new_category)
    await callback.message.edit_text(
        "✍️ Send the new category name:", reply_markup=cancel_keyboard()
    )
    await callback.answer()


@router.message(AddTransaction.new_category)
async def add_new_category_name(
    message: Message, state: FSMContext, category_service: CategoryService
):
    data = await state.get_data()
    category_id = await category_service.add(
        message.from_user.id, (message.text or "").strip()[:50], data["type"]
    )
    await state.update_data(category_id=category_id)
    await state.set_state(AddTransaction.note)
    await message.answer("📝 Send a note, or skip:", reply_markup=skip_note_keyboard())


async def _finalize(
    target,
    user_id: int,
    state: FSMContext,
    transaction_service: TransactionService,
    chart_service: ChartService,
    note: str | None,
    *,
    edit: bool,
) -> None:
    data = await state.get_data()
    amount = Decimal(data["amount"])
    type_ = data["type"]
    category_id = data["category_id"]
    try:
        await transaction_service.add(user_id, category_id, amount, note)
    except Exception:
        logger.exception("Failed to save transaction")
        await state.clear()
        await (target.edit_text if edit else target.answer)(
            "⚠️ Couldn't save this transaction. Please try /add again."
        )
        return
    sign = "➕" if type_ == "income" else "➖"
    text = (
        f"✅ Saved!\n"
        f"{sign} {format_money(amount)}\n"
        f"Note: {html.escape(note) if note else '—'}"
    )
    if type_ == "expense":
        breach = await transaction_service.check_limit(user_id, category_id)
        if breach:
            text += (
                f"\n\n⚠️ Limit exceeded! Spent {format_money(breach['spent'])} "
                f"of {format_money(breach['limit'])} this month."
            )
    await (target.edit_text if edit else target.answer)(text)
    await state.clear()
    await send_stats_chart(
        target, user_id, transaction_service, chart_service, caption="📊 Your month so far"
    )


@router.callback_query(AddTransaction.note, F.data == "add:skip")
async def add_note_skip(
    callback: CallbackQuery,
    state: FSMContext,
    transaction_service: TransactionService,
    chart_service: ChartService,
):
    await _finalize(
        callback.message,
        callback.from_user.id,
        state,
        transaction_service,
        chart_service,
        None,
        edit=True,
    )
    await callback.answer()


@router.message(AddTransaction.note)
async def add_note_text(
    message: Message,
    state: FSMContext,
    transaction_service: TransactionService,
    chart_service: ChartService,
):
    await _finalize(
        message,
        message.from_user.id,
        state,
        transaction_service,
        chart_service,
        (message.text or "").strip(),
        edit=False,
    )


@router.callback_query(F.data == "add:cancel")
async def add_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Cancelled.")
    await callback.answer()


@router.message(Command("history"))
async def cmd_history(message: Message, transaction_service: TransactionService):
    transactions = await transaction_service.last_transactions(message.from_user.id)
    if not transactions:
        await message.answer("No transactions yet. Use /add.")
        return

    lines = ["🧾 <b>Last transactions</b>\n"]
    for transaction in transactions:
        sign = (
            "➕"
            if transaction["type"] == "income"
            else "➖"
            if transaction["type"] == "expense"
            else "•"
        )
        when = transaction["created_at"].strftime("%Y-%m-%d %H:%M")
        category = (
            html.escape(transaction["category"]) if transaction["category"] else "—"
        )
        note = (
            f" — {html.escape(transaction['note'])}" if transaction["note"] else ""
        )
        lines.append(
            f"{sign} {format_money(transaction['amount'])} | {category} | {when}{note}"
        )
    await message.answer("\n".join(lines))


@router.message(Command("report"))
async def cmd_report(message: Message, transaction_service: TransactionService):
    rows = await transaction_service.current_month_transactions(message.from_user.id)
    if not rows:
        await message.answer("No transactions this month to export.")
        return

    file_descriptor, path = tempfile.mkstemp(suffix=".csv", prefix="report_")
    try:
        with os.fdopen(file_descriptor, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["date", "category", "type", "amount", "note"])
            for row in rows:
                writer.writerow(
                    [
                        row["created_at"].strftime("%Y-%m-%d %H:%M"),
                        row["category"] or "",
                        row["type"] or "",
                        f"{row['amount']:.2f}",
                        row["note"] or "",
                    ]
                )
        await message.answer_document(
            FSInputFile(path, filename="monthly_report.csv"),
            caption="📊 This month's transactions",
        )
    finally:
        os.remove(path)
