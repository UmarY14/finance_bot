import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from handlers.transactions import format_money, parse_amount
from keyboards.inline import (
    categories_menu_keyboard,
    category_type_keyboard,
    confirm_delete_keyboard,
    delete_category_keyboard,
    limit_category_keyboard,
)
from services.category_service import CategoryService
from services.transaction_service import TransactionService


router = Router()


class AddCategory(StatesGroup):
    name = State()
    type = State()


class SetLimit(StatesGroup):
    amount = State()


def _render_categories(categories: list[dict]) -> str:
    if not categories:
        return "📂 You have no categories yet. Add one below."

    income = [category for category in categories if category["type"] == "income"]
    expense = [category for category in categories if category["type"] == "expense"]
    lines = ["📂 <b>Your categories</b>\n"]
    if income:
        lines.append(
            "💰 <b>Income</b>: "
            + ", ".join(html.escape(category["name"]) for category in income)
        )
    if expense:
        lines.append(
            "💸 <b>Expense</b>: "
            + ", ".join(html.escape(category["name"]) for category in expense)
        )
    return "\n".join(lines)


@router.message(Command("categories"))
async def cmd_categories(message: Message, category_service: CategoryService):
    categories = await category_service.list_all(message.from_user.id)
    await message.answer(
        _render_categories(categories), reply_markup=categories_menu_keyboard()
    )


@router.callback_query(F.data == "cat:add")
async def cat_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddCategory.name)
    await callback.message.answer("✍️ Send the new category name:")
    await callback.answer()


@router.message(AddCategory.name)
async def cat_add_name(message: Message, state: FSMContext):
    await state.update_data(name=(message.text or "").strip()[:50])
    await state.set_state(AddCategory.type)
    await message.answer("Choose its type:", reply_markup=category_type_keyboard())


@router.callback_query(AddCategory.type, F.data.startswith("catadd:"))
async def cat_add_type(
    callback: CallbackQuery, state: FSMContext, category_service: CategoryService
):
    type_ = callback.data.split(":")[1]
    data = await state.get_data()
    await category_service.add(callback.from_user.id, data["name"], type_)
    await state.clear()
    await callback.message.edit_text(
        f"✅ Category '{html.escape(data['name'])}' added ({type_})."
    )
    await callback.answer()


@router.callback_query(F.data == "cat:del")
async def cat_del(callback: CallbackQuery, category_service: CategoryService):
    categories = await category_service.list_all(callback.from_user.id)
    if not categories:
        await callback.answer("No categories to delete.", show_alert=True)
        return

    await callback.message.edit_text(
        "Select a category to delete:",
        reply_markup=delete_category_keyboard(categories),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("catdel:"))
async def cat_del_pick(callback: CallbackQuery, category_service: CategoryService):
    category_id = int(callback.data.split(":")[1])
    category = await category_service.get(category_id, callback.from_user.id)
    if not category:
        await callback.answer("Not found.", show_alert=True)
        return

    await callback.message.edit_text(
        f"Delete '{html.escape(category['name'])}'? "
        "Existing transactions are kept (category cleared).",
        reply_markup=confirm_delete_keyboard(category_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("catdelok:"))
async def cat_del_confirm(
    callback: CallbackQuery, category_service: CategoryService
):
    category_id = int(callback.data.split(":")[1])
    await category_service.delete(category_id, callback.from_user.id)
    await callback.message.edit_text("🗑 Category deleted.")
    await callback.answer()


@router.callback_query(F.data.in_({"cat:close", "cat:cancel"}))
async def cat_close(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("✖ Closed.")
    await callback.answer()


@router.message(Command("limit"))
async def cmd_limit(message: Message, category_service: CategoryService):
    categories = await category_service.list_by_type(message.from_user.id, "expense")
    if not categories:
        await message.answer("Create an expense category first via /categories.")
        return

    await message.answer(
        "Select an expense category to set a monthly limit:",
        reply_markup=limit_category_keyboard(categories),
    )


@router.callback_query(F.data.startswith("lim:cat:"))
async def limit_pick(callback: CallbackQuery, state: FSMContext):
    await state.update_data(limit_category_id=int(callback.data.split(":")[2]))
    await state.set_state(SetLimit.amount)
    await callback.message.edit_text("Enter the monthly limit amount (send 0 to clear):")
    await callback.answer()


@router.message(SetLimit.amount)
async def limit_amount(
    message: Message, state: FSMContext, transaction_service: TransactionService
):
    data = await state.get_data()
    category_id = data["limit_category_id"]
    if (message.text or "").strip() == "0":
        await transaction_service.delete_limit(message.from_user.id, category_id)
        await state.clear()
        await message.answer("✅ Limit cleared.")
        return

    amount = parse_amount(message.text)
    if amount is None:
        await message.answer("⚠️ Invalid. Send a positive number, or 0 to clear:")
        return

    await transaction_service.set_limit(message.from_user.id, category_id, amount)
    await state.clear()
    await message.answer(f"✅ Monthly limit set: {format_money(amount)}")


@router.callback_query(F.data == "lim:cancel")
async def limit_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Cancelled.")
    await callback.answer()
