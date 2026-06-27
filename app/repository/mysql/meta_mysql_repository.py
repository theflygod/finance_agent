"""Meta MySQL repository for table_info, column_info, metric_info, column_metric."""

from __future__ import annotations

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL


class MetaMysqlRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_table_infos(self, table_infos: list[TableInfoMySQL]) -> None:
        self.session.add_all(table_infos)

    async def save_column_infos(self, column_infos: list[ColumnInfoMySQL]) -> None:
        self.session.add_all(column_infos)

    async def save_metric_infos(self, metric_infos: list[MetricInfoMySQL]) -> None:
        self.session.add_all(metric_infos)

    async def save_column_metrics(self, column_metrics: list[ColumnMetricMySQL]) -> None:
        self.session.add_all(column_metrics)

    async def get_column_info_by_id(self, column_id: str) -> ColumnInfoMySQL | None:
        return await self.session.get(ColumnInfoMySQL, column_id)

    async def get_table_info_by_id(self, table_id: str) -> TableInfoMySQL | None:
        return await self.session.get(TableInfoMySQL, table_id)

    async def get_key_columns_by_table_id(self, table_id: str) -> list[ColumnInfoMySQL]:
        sql = """
            SELECT * FROM column_info
            WHERE table_id = :table_id AND role IN ('primary_key', 'foreign_key')
        """
        query = select(ColumnInfoMySQL).from_statement(text(sql))
        result = await self.session.execute(query, {"table_id": table_id})
        return result.scalars().fetchall()

    async def get_all_table_infos(self) -> list[TableInfoMySQL]:
        result = await self.session.execute(select(TableInfoMySQL))
        return result.scalars().fetchall()

    async def get_all_key_columns(self) -> list[ColumnInfoMySQL]:
        sql = """
            SELECT * FROM column_info
            WHERE role IN ('primary_key', 'foreign_key')
        """
        query = select(ColumnInfoMySQL).from_statement(text(sql))
        result = await self.session.execute(query)
        return result.scalars().fetchall()

    async def get_columns_by_table_id(self, table_id: str) -> list[ColumnInfoMySQL]:
        sql = """
            SELECT * FROM column_info
            WHERE table_id = :table_id
        """
        query = select(ColumnInfoMySQL).from_statement(text(sql))
        result = await self.session.execute(query, {"table_id": table_id})
        return result.scalars().fetchall()