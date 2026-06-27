"""Value ES repository for full-text search on dimension values."""

from __future__ import annotations

from elasticsearch import AsyncElasticsearch

from app.models.es.value_info_es import ValueInfoEs


class ValueEsRepository:

    es_index_name = "finance_agent_values"
    es_index_mappings = {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
            "type": {"type": "keyword"},
            "column_id": {"type": "keyword"},
            "column_name": {"type": "keyword"},
            "table_id": {"type": "keyword"},
            "table_name": {"type": "keyword"},
        },
    }

    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def ensure_index(self) -> None:
        if not await self.client.indices.exists(index=self.es_index_name):
            await self.client.indices.create(
                index=self.es_index_name,
                mappings=self.es_index_mappings,
            )

    async def upsert_values(self, value_infos: list[ValueInfoEs], batch_size: int = 20) -> None:
        for i in range(0, len(value_infos), batch_size):
            operations = []
            batch = value_infos[i : i + batch_size]
            for v in batch:
                operations.append({"index": {"_index": self.es_index_name}})
                operations.append(v.__dict__)
            await self.client.bulk(operations=operations)

    async def search(self, keyword: str, limit: int = 10) -> list[dict]:
        resp = await self.client.search(
            index=self.es_index_name,
            query={"match": {"value": keyword}},
            size=limit,
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]