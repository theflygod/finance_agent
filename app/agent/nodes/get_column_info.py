"""Node: retrieve column info from Qdrant vector search + MySQL supplement."""

from __future__ import annotations

from loguru import logger

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.repository.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository

MAX_COLUMNS = 100


async def get_column_info(state: AgentState, context: AgentContext) -> dict:
    question = state.rewritten_question
    embedding = await context.embedding.aembed_query(question)
    repo = ColumnQdrantRepository(context.qdrant_client)
    results = await repo.search(embedding=embedding, limit=20)

    final_table_names = {t.get("name", "") for t in state.table_info}

    results = [r for r in results if r.get("table_name", "") in final_table_names]

    vector_table_names = {r.get("table_name", "") for r in results}
    missing_tables = []
    for t in state.table_info:
        tname = t.get("name", "")
        if tname and tname not in vector_table_names:
            missing_tables.append(t)

    if missing_tables:
        async with context.meta_session_factory() as session:
            repo_mysql = MetaMysqlRepository(session)
            for t in missing_tables:
                tid = t.get("id", "")
                tname = t.get("name", "")
                if not tid:
                    continue
                cols = await repo_mysql.get_columns_by_table_id(tid)
                for col in cols:
                    if col.role in ("primary_key", "foreign_key", "dimension", "measure"):
                        results.append(
                            {
                                "id": col.id,
                                "name": col.name,
                                "role": col.role,
                                "description": col.description or "",
                                "alias": col.alias if col.alias else [],
                                "table_id": col.table_id,
                                "table_name": tname,
                            }
                        )
        logger.info(f"get_column_info: supplemented key/dim/measure columns for {len(missing_tables)} tables from MySQL")

    if len(results) > MAX_COLUMNS:
        priority = []
        normal = []
        for r in results:
            role = r.get("role", "")
            if role in ("primary_key", "foreign_key", "measure"):
                priority.append(r)
            else:
                normal.append(r)
        results = priority + normal[:MAX_COLUMNS - len(priority)]

    logger.info(f"get_column_info: returning {len(results)} columns for {len(final_table_names)} tables")
    return {"column_info": results}