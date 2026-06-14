from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


CANCEL_CB = "add:cancel"


def type_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Income", callback_data="add:type:income")
    kb.button(text="💸 Expense", callback_data="add:type:expense")
    kb.button(text="❌ Cancel", callback_data=CANCEL_CB)
    kb.adjust(2, 1)
    return kb.as_markup()


def category_keyboard(categories: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category["name"], callback_data=f"add:cat:{category['id']}")
    kb.button(text="➕ New category", callback_data="add:newcat")
    kb.button(text="❌ Cancel", callback_data=CANCEL_CB)
    kb.adjust(2)
    return kb.as_markup()


def skip_note_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⏭ Skip", callback_data="add:skip")
    kb.button(text="❌ Cancel", callback_data=CANCEL_CB)
    kb.adjust(2)
    return kb.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Cancel", callback_data=CANCEL_CB)
    return kb.as_markup()


def categories_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Add", callback_data="cat:add")
    kb.button(text="🗑 Delete", callback_data="cat:del")
    kb.button(text="✖ Close", callback_data="cat:close")
    kb.adjust(2, 1)
    return kb.as_markup()


def category_type_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Income", callback_data="catadd:income")
    kb.button(text="💸 Expense", callback_data="catadd:expense")
    kb.button(text="❌ Cancel", callback_data="cat:cancel")
    kb.adjust(2, 1)
    return kb.as_markup()


def delete_category_keyboard(categories: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(
            text=f"{category['name']} ({category['type']})",
            callback_data=f"catdel:{category['id']}",
        )
    kb.button(text="❌ Cancel", callback_data="cat:cancel")
    kb.adjust(1)
    return kb.as_markup()


def confirm_delete_keyboard(category_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Yes, delete", callback_data=f"catdelok:{category_id}")
    kb.button(text="❌ No", callback_data="cat:cancel")
    kb.adjust(2)
    return kb.as_markup()


def limit_category_keyboard(categories: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in categories:
        kb.button(text=category["name"], callback_data=f"lim:cat:{category['id']}")
    kb.button(text="❌ Cancel", callback_data="lim:cancel")
    kb.adjust(2)
    return kb.as_markup()
