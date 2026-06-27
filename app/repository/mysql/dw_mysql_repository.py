"""Data warehouse MySQL repository for querying DW tables."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DwMysqlRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        sql = f"SHOW COLUMNS FROM {table_name}"
        result = await self.session.execute(text(sql))
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values(self, table_name: str, column_name: str, limit: int = 10) -> list[str]:
        sql = f"SELECT DISTINCT {column_name} FROM {table_name} LIMIT {limit}"
        result = await self.session.execute(text(sql))
        return result.scalars().fetchall()

    async def get_db_info(self) -> dict[str, str]:
        result = await self.session.execute(text("SELECT version()"))
        version = result.scalar()
        dialect = self.session.get_bind().dialect.name
        return {"version": version, "dialect": dialect}

    async def validate_sql(self, sql: str) -> None:
        await self.session.execute(text(f"EXPLAIN {sql}"))

    async def execute_sql(self, sql: str) -> list[dict]:
        result = await self.session.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]