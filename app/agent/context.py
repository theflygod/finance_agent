"""Agent context: shared resources for all nodes."""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel
from qdrant_client import AsyncQdrantClient
from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.clients.embedding_client_manager import EmbeddingClient


@dataclass
class AgentContext:
    llm: BaseChatModel
    embedding: EmbeddingClient
    qdrant_client: AsyncQdrantClient
    es_client: AsyncElasticsearch
    dw_session_factory: async_sessionmaker[AsyncSession]
    meta_session_factory: async_sessionmaker[AsyncSession]