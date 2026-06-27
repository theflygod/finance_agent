"""Async MySQL client manager using SQLAlchemy + asyncmy."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.conf.app_config import DBConfig, MetaDBConfig, app_config

# 使用 SQLAlchemy + asyncmy 驱动 创建异步连接池。
class MySQLClientManager:

    def __init__(self, db_config: DBConfig | MetaDBConfig):
        self.db_config = db_config
        self.engine = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def _get_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.db_config.user}:{self.db_config.password}"
            f"@{self.db_config.host}:{self.db_config.port}/{self.db_config.database}"
            f"?charset={self.db_config.charset}"
        )

    def init(self) -> None:
        self.engine = create_async_engine(self._get_url(), echo=False, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    @asynccontextmanager
    async def session_factory_ctx(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def close(self) -> None:
        if self.engine:
            await self.engine.dispose()


dw_mysql_client_manager = MySQLClientManager(app_config.dw_db)
meta_mysql_client_manager = MySQLClientManager(app_config.meta_db)