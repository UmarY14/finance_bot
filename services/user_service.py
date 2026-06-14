from db import queries
from db.connection import Database


DEFAULT_CATEGORIES = [
    ("Salary", "income"),
    ("Other income", "income"),
    ("Food", "expense"),
    ("Transport", "expense"),
    ("Bills", "expense"),
    ("Shopping", "expense"),
]


class UserService:
    def __init__(self, db: Database):
        self.db = db

    async def get(self, user_id: int) -> dict | None:
        row = await self.db.fetchrow(queries.GET_USER, user_id)
        return dict(row) if row else None

    async def register(self, user_id: int, name: str) -> bool:
        existing = await self.get(user_id)
        if existing:
            return False

        await self.db.execute(queries.INSERT_USER, user_id, name)
        for category_name, category_type in DEFAULT_CATEGORIES:
            await self.db.execute(
                queries.INSERT_CATEGORY, user_id, category_name, category_type
            )
        return True
