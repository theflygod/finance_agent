"""Script to build meta knowledge base (MySQL + Qdrant + ES)."""

import asyncio

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.services.meta_knowledge_service import meta_knowledge_service


async def main():
    qdrant_client_manager.init()
    es_client_manager.init()
    embedding_client_manager.init()
    meta_mysql_client_manager.init()

    try:
        await meta_knowledge_service.build_all()
    finally:
        await qdrant_client_manager.close()
        await es_client_manager.close()
        await meta_mysql_client_manager.close()


if __name__ == "__main__":
    asyncio.run(main())