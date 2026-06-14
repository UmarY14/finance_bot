from db import queries
from db.connection import Database


class CategoryService:
    def __init__(self, db: Database):
        self.db = db

    async def list_all(self, user_id: int) -> list[dict]:
        rows = await self.db.fetch(queries.GET_CATEGORIES_BY_USER, user_id)
        return [dict(row) for row in rows]

    async def list_by_type(self, user_id: int, type_: str) -> list[dict]:
        rows = await self.db.fetch(queries.GET_CATEGORIES_BY_TYPE, user_id, type_)
        return [dict(row) for row in rows]

    async def get(self, category_id: int, user_id: int) -> dict | None:
        row = await self.db.fetchrow(queries.GET_CATEGORY, category_id, user_id)
        return dict(row) if row else None

    async def add(self, user_id: int, name: str, type_: str) -> int:
        return await self.db.fetchval(queries.INSERT_CATEGORY, user_id, name, type_)

    async def delete(self, category_id: int, user_id: int) -> None:
        await self.db.execute(queries.DELETE_CATEGORY, category_id, user_id)
