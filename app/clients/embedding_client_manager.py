"""Embedding client manager for HuggingFace TEI service."""

from __future__ import annotations

from typing import Optional

import httpx
from loguru import logger

from app.conf.app_config import EmbeddingConfig, app_config

# 调用独立的 HuggingFace TEI（Text Embedding Inference）服务，把用户问题转成向量
class EmbeddingClientManager:

    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: Optional[EmbeddingClient] = None

    def _get_url(self) -> str:
        return f"http://{self.config.host}:{self.config.port}"

    def init(self) -> None:
        self.client = EmbeddingClient(base_url=self._get_url())


class EmbeddingClient:

    def __init__(self, base_url: str, batch_size: int = 4):
        self.base_url = base_url.rstrip("/")
        self.batch_size = batch_size
        self._max_text_len = 200

    async def aembed_query(self, text: str) -> list[float]:
        result = await self.aembed_documents([text])
        return result[0]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        import asyncio
        truncated = [t[:self._max_text_len] for t in texts]
        all_embeddings: list[list[float]] = []
        async with httpx.AsyncClient(timeout=300.0) as http:
            for i in range(0, len(truncated), self.batch_size):
                batch = truncated[i : i + self.batch_size]
                for attempt in range(3):
                    try:
                        resp = await http.post(
                            f"{self.base_url}/embed",
                            json={"inputs": batch},
                        )
                        resp.raise_for_status()
                        all_embeddings.extend(resp.json())
                        break
                    except (httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.HTTPStatusError) as e:
                        if attempt == 2:
                            raise
                        logger.warning(f"Embedding batch {i//self.batch_size} failed (attempt {attempt+1}): {e}, retrying...")
                        await asyncio.sleep(2 ** attempt)
        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        result = self.embed_documents([text])
        return result[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        all_embeddings: list[list[float]] = []
        with httpx.Client(timeout=120.0) as http:
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i : i + self.batch_size]
                resp = http.post(
                    f"{self.base_url}/embed",
                    json={"inputs": batch},
                )
                resp.raise_for_status()
                all_embeddings.extend(resp.json())
        return all_embeddings


embedding_client_manager = EmbeddingClientManager(app_config.embedding)