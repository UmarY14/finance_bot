from pathlib import Path

import asyncpg


class Database:
    def __init__(self, dsn: str):
        self._dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(dsn=self._dsn, min_size=1, max_size=10)

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()

    async def migrate(self) -> None:
        schema = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
        async with self.pool.acquire() as conn:
            await conn.execute(schema)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def execute(self, query: str, *args) -> str:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
