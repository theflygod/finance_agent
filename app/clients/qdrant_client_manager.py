"""Qdrant async client manager."""

from __future__ import annotations

from typing import Optional

from qdrant_client import AsyncQdrantClient

from app.conf.app_config import QdrantConfig, app_config

# 创建 Qdrant 异步客户端，后面用作向量检索（查相似的表、字段）。
class QdrantClientManager:

    def __init__(self, qdrant_config: QdrantConfig):
        self.qdrant_config = qdrant_config
        self.client: Optional[AsyncQdrantClient] = None

    def _get_url(self) -> str:
        return f"http://{self.qdrant_config.host}:{self.qdrant_config.port}"

    def init(self) -> None:
        self.client = AsyncQdrantClient(self._get_url())

    async def close(self) -> None:
        if self.client:
            await self.client.close()


qdrant_client_manager = QdrantClientManager(app_config.qdrant)