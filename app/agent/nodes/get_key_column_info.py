"""Node: retrieve key column info (primary/foreign keys) from MySQL meta."""

from __future__ import annotations

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.repository.mysql.meta_mysql_repository import MetaMysqlRepository


async def get_key_column_info(state: AgentState, context: AgentContext) -> dict:
    table_name_to_id = {t.get("name", ""): t.get("id", "") for t in state.table_info}
    table_id_to_name = {v: k for k, v in table_name_to_id.items()}
    all_key_cols = []
    async with context.meta_session_factory() as session:
        repo = MetaMysqlRepository(session)
        for table_name, table_id in table_name_to_id.items():
            if not table_id:
                continue
            key_cols = await repo.get_key_columns_by_table_id(table_id)
            for col in key_cols:
                desc = col.description or ""
                all_key_cols.append(
                    {
                        "table_name": table_name,
                        "column_name": col.name,
                        "role": col.role,
                        "description": desc,
                    }
                )
    return {"key_column_info": all_key_cols}