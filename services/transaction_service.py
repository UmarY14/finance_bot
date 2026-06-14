from decimal import Decimal

from db import queries
from db.connection import Database


class TransactionService:
    def __init__(self, db: Database):
        self.db = db

    async def add(
        self, user_id: int, category_id: int, amount: Decimal, note: str | None
    ) -> dict:
        row = await self.db.fetchrow(
            queries.INSERT_TRANSACTION, user_id, category_id, amount, note
        )
        return dict(row)

    async def monthly_stats(self, user_id: int) -> dict:
        row = await self.db.fetchrow(queries.MONTHLY_STATS, user_id)
        income = row["income"]
        expense = row["expense"]
        return {"income": income, "expense": expense, "net": income - expense}

    async def last_transactions(self, user_id: int) -> list[dict]:
        rows = await self.db.fetch(queries.LAST_TRANSACTIONS, user_id)
        return [dict(row) for row in rows]

    async def monthly_comparison(self, user_id: int) -> list[dict]:
        rows = await self.db.fetch(queries.MONTHLY_COMPARISON, user_id)
        return [dict(row) for row in rows]

    async def current_month_transactions(self, user_id: int) -> list[dict]:
        rows = await self.db.fetch(queries.CURRENT_MONTH_TRANSACTIONS, user_id)
        return [dict(row) for row in rows]

    async def expense_by_category(self, user_id: int) -> list[dict]:
        rows = await self.db.fetch(queries.MONTHLY_EXPENSE_BY_CATEGORY, user_id)
        return [dict(row) for row in rows]

    async def category_month_spent(self, user_id: int, category_id: int) -> Decimal:
        return await self.db.fetchval(
            queries.CATEGORY_MONTH_SPENT, user_id, category_id
        )

    async def set_limit(
        self, user_id: int, category_id: int, amount: Decimal
    ) -> None:
        await self.db.execute(queries.UPSERT_LIMIT, user_id, category_id, amount)

    async def get_limit(self, user_id: int, category_id: int) -> Decimal | None:
        return await self.db.fetchval(queries.GET_LIMIT, user_id, category_id)

    async def delete_limit(self, user_id: int, category_id: int) -> None:
        await self.db.execute(queries.DELETE_LIMIT, user_id, category_id)

    async def list_limits(self, user_id: int) -> list[dict]:
        rows = await self.db.fetch(queries.GET_LIMITS, user_id)
        return [dict(row) for row in rows]

    async def check_limit(self, user_id: int, category_id: int) -> dict | None:
        limit = await self.get_limit(user_id, category_id)
        if limit is None:
            return None

        spent = await self.category_month_spent(user_id, category_id)
        if spent > limit:
            return {"limit": limit, "spent": spent}
        return None
