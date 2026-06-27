"""Meta knowledge service: build knowledge base from meta_config.yaml into MySQL, Qdrant, ES."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from loguru import logger
from omegaconf import OmegaConf

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.conf.app_config import ROOT_DIR
from app.conf.meta_config import MetaConfig
from app.models.es.value_info_es import ValueInfoEs
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.mysql.base import Base
from app.repository.es.value_es_repository import ValueEsRepository
from app.repository.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repository.qdrant.metric_qdrant_repository import MetricQdrantRepository


def _generate_id(*parts: str) -> str:
    return hashlib.md5("_".join(parts).encode()).hexdigest()[:16]


def _generate_uuid(*parts: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, "_".join(parts)))


class MetaKnowledgeService:

    def __init__(self):
        self.meta_config: MetaConfig | None = None
        self.column_qdrant_repo: ColumnQdrantRepository | None = None
        self.metric_qdrant_repo: MetricQdrantRepository | None = None
        self.value_es_repo: ValueEsRepository | None = None

    def load_config(self) -> None:
        config_path = ROOT_DIR / "conf" / "meta_config.yaml"
        raw = OmegaConf.load(config_path)
        self.meta_config = OmegaConf.to_object(OmegaConf.merge(OmegaConf.structured(MetaConfig), raw))
        logger.info(f"Loaded meta config with {len(self.meta_config.tables)} tables, {len(self.meta_config.metrics)} metrics")

    async def build_mysql(self) -> None:
        async with meta_mysql_client_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("MySQL meta tables created")

        table_infos: list[TableInfoMySQL] = []
        column_infos: list[ColumnInfoMySQL] = []
        column_metrics: list[ColumnMetricMySQL] = []

        for table_cfg in self.meta_config.tables:
            table_id = _generate_id(table_cfg.name)
            table_infos.append(
                TableInfoMySQL(
                    id=table_id,
                    name=table_cfg.name,
                    role=table_cfg.role,
                    description=table_cfg.description,
                )
            )
            for col_cfg in table_cfg.columns:
                col_id = _generate_id(table_cfg.name, col_cfg.name)
                column_infos.append(
                    ColumnInfoMySQL(
                        id=col_id,
                        name=col_cfg.name,
                        type="",
                        role=col_cfg.role,
                        examples=[],
                        description=col_cfg.description,
                        alias=col_cfg.alias if col_cfg.alias else [],
                        table_id=table_id,
                    )
                )

        for metric_cfg in self.meta_config.metrics:
            metric_id = _generate_id("metric", metric_cfg.name)
            for col_ref in metric_cfg.relevant_columns:
                parts = col_ref.split(".")
                if len(parts) == 2:
                    col_id = _generate_id(parts[0], parts[1])
                    column_metrics.append(
                        ColumnMetricMySQL(column_id=col_id, metric_id=metric_id)
                    )

        async with meta_mysql_client_manager.session_factory_ctx() as session:
            from sqlalchemy import text
            await session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            await session.execute(text("TRUNCATE TABLE column_metric"))
            await session.execute(text("TRUNCATE TABLE metric_info"))
            await session.execute(text("TRUNCATE TABLE column_info"))
            await session.execute(text("TRUNCATE TABLE table_info"))
            await session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            repo = MetaMysqlRepository(session)
            await repo.save_table_infos(table_infos)
            await repo.save_column_infos(column_infos)
            await repo.save_column_metrics(column_metrics)

            metric_infos = []
            for metric_cfg in self.meta_config.metrics:
                metric_id = _generate_id("metric", metric_cfg.name)
                metric_infos.append(
                    MetricInfoMySQL(
                        id=metric_id,
                        name=metric_cfg.name,
                        description=metric_cfg.description,
                        relevant_columns=metric_cfg.relevant_columns if metric_cfg.relevant_columns else [],
                        alias=metric_cfg.alias if metric_cfg.alias else [],
                    )
                )
            await repo.save_metric_infos(metric_infos)
            await session.commit()

        logger.info(f"MySQL meta data built: {len(table_infos)} tables, {len(column_infos)} columns")

    async def build_qdrant(self) -> None:
        self.column_qdrant_repo = ColumnQdrantRepository(qdrant_client_manager.client)
        self.metric_qdrant_repo = MetricQdrantRepository(qdrant_client_manager.client)
        await self.column_qdrant_repo.ensure_collection()
        await self.metric_qdrant_repo.ensure_collection()

        col_ids, col_texts, col_payloads = [], [], []
        for table_cfg in self.meta_config.tables:
            table_id = _generate_id(table_cfg.name)
            for col_cfg in table_cfg.columns:
                col_id = _generate_id(table_cfg.name, col_cfg.name)
                col_uuid = _generate_uuid(table_cfg.name, col_cfg.name)
                alias_str = ", ".join(col_cfg.alias) if col_cfg.alias else ""
                text = f"表名: {table_cfg.name}, 表描述: {table_cfg.description}, 列名: {col_cfg.name}, 列描述: {col_cfg.description}, 别名: {alias_str}"
                col_ids.append(col_uuid)
                col_texts.append(text)
                col_payloads.append(
                    {
                        "id": col_id,
                        "name": col_cfg.name,
                        "role": col_cfg.role,
                        "description": col_cfg.description,
                        "alias": col_cfg.alias if col_cfg.alias else [],
                        "table_id": table_id,
                        "table_name": table_cfg.name,
                    }
                )

        col_embeddings = await self._embed_texts(col_texts)
        await self.column_qdrant_repo.upsert_embedding(col_ids, col_embeddings, col_payloads)
        logger.info(f"Qdrant column vectors built: {len(col_ids)}")

        met_ids, met_texts, met_payloads = [], [], []
        for metric_cfg in self.meta_config.metrics:
            metric_id = _generate_id("metric", metric_cfg.name)
            metric_uuid = _generate_uuid("metric", metric_cfg.name)
            alias_str = ", ".join(metric_cfg.alias) if metric_cfg.alias else ""
            cols_str = ", ".join(metric_cfg.relevant_columns) if metric_cfg.relevant_columns else ""
            text = f"指标名: {metric_cfg.name}, 指标描述: {metric_cfg.description}, 别名: {alias_str}, 关联字段: {cols_str}"
            met_ids.append(metric_uuid)
            met_texts.append(text)
            met_payloads.append(
                {
                    "id": metric_id,
                    "name": metric_cfg.name,
                    "description": metric_cfg.description,
                    "relevant_columns": metric_cfg.relevant_columns if metric_cfg.relevant_columns else [],
                    "alias": metric_cfg.alias if metric_cfg.alias else [],
                }
            )

        met_embeddings = await self._embed_texts(met_texts)
        await self.metric_qdrant_repo.upsert_embeddings(met_ids, met_embeddings, met_payloads)
        logger.info(f"Qdrant metric vectors built: {len(met_ids)}")

    async def build_es(self) -> None:
        self.value_es_repo = ValueEsRepository(es_client_manager.client)
        await self.value_es_repo.ensure_index()

        value_infos: list[ValueInfoEs] = []
        for table_cfg in self.meta_config.tables:
            table_id = _generate_id(table_cfg.name)
            for col_cfg in table_cfg.columns:
                if not col_cfg.sync:
                    continue
                col_id = _generate_id(table_cfg.name, col_cfg.name)
                if col_cfg.alias:
                    for alias in col_cfg.alias:
                        value_infos.append(
                            ValueInfoEs(
                                id=_generate_id(col_id, alias),
                                value=alias,
                                type="alias",
                                column_id=col_id,
                                column_name=col_cfg.name,
                                table_id=table_id,
                                table_name=table_cfg.name,
                            )
                        )
                value_infos.append(
                    ValueInfoEs(
                        id=_generate_id(col_id, col_cfg.name),
                        value=col_cfg.name,
                        type="column_name",
                        column_id=col_id,
                        column_name=col_cfg.name,
                        table_id=table_id,
                        table_name=table_cfg.name,
                    )
                )

        db_values = await self._fetch_db_dimension_values()
        value_infos.extend(db_values)

        await self.value_es_repo.upsert_values(value_infos)
        logger.info(f"ES value index built: {len(value_infos)} docs")

    async def _fetch_db_dimension_values(self) -> list[ValueInfoEs]:
        import pymysql
        from app.conf.app_config import app_config

        value_infos: list[ValueInfoEs] = []
        db_cfg = app_config.dw_db
        conn = pymysql.connect(
            host=db_cfg.host,
            port=db_cfg.port,
            user=db_cfg.user,
            password=db_cfg.password,
            database=db_cfg.database,
        )
        cursor = conn.cursor()

        for table_cfg in self.meta_config.tables:
            table_id = _generate_id(table_cfg.name)
            for col_cfg in table_cfg.columns:
                if col_cfg.role not in ("dimension",):
                    continue
                try:
                    sql = f"SELECT DISTINCT `{col_cfg.name}` FROM `{table_cfg.name}` WHERE `{col_cfg.name}` IS NOT NULL LIMIT 100"
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    col_id = _generate_id(table_cfg.name, col_cfg.name)
                    for row in rows:
                        val = str(row[0])
                        if len(val) > 200:
                            continue
                        value_infos.append(
                            ValueInfoEs(
                                id=_generate_id(col_id, "dbval", val),
                                value=val,
                                type="db_value",
                                column_id=col_id,
                                column_name=col_cfg.name,
                                table_id=table_id,
                                table_name=table_cfg.name,
                            )
                        )
                except Exception:
                    pass

        conn.close()
        logger.info(f"Fetched {len(value_infos)} dimension values from database")
        return value_infos

    async def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = await embedding_client_manager.client.aembed_documents(texts)
        return embeddings

    async def build_all(self) -> None:
        self.load_config()
        await self.build_mysql()
        await self.build_qdrant()
        await self.build_es()
        logger.info("Meta knowledge base built successfully!")


meta_knowledge_service = MetaKnowledgeService()