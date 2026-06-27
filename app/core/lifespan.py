"""FastAPI application lifespan: init and teardown all clients."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.core.log import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting up finance-data application...")

    qdrant_client_manager.init()
    es_client_manager.init()
    embedding_client_manager.init()
    dw_mysql_client_manager.init()
    meta_mysql_client_manager.init()

    logger.info("All clients initialized")

    yield

    logger.info("Shutting down finance-data application...")

    await qdrant_client_manager.close()
    await es_client_manager.close()
    await dw_mysql_client_manager.close()
    await meta_mysql_client_manager.close()

    logger.info("All clients closed")