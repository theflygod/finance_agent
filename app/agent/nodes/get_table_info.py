"""Node: retrieve table info from Qdrant vector search."""

from __future__ import annotations

from loguru import logger

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.repository.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository

MAX_VECTOR_TABLES = 5
MAX_TOTAL_TABLES = 10


def _is_join_table(name: str) -> bool:
    return name.startswith("dim_") or name in ("customer",)


def _is_core_fact_table(name: str) -> bool:
    return name in (
        "loan_contract", "loan_application", "loan_disbursement",
        "repayment_record", "repayment_schedule", "credit_limit",
        "credit_application", "overdue_record", "collection_case",
        "bank_account", "bank_card", "business_stat_daily",
    )


def _infer_referenced_table(col_name: str, all_table_names: set[str]) -> str | None:
    if col_name == "id":
        return None
    for suffix in ("_id", "_code", "_key"):
        if col_name.endswith(suffix):
            prefix = col_name[: -len(suffix)]
            candidates = []
            for tn in all_table_names:
                tn_lower = tn.lower()
                if tn_lower == prefix:
                    candidates.append(tn)
                elif tn_lower == f"dim_{prefix}":
                    candidates.append(tn)
            if len(candidates) == 1:
                return candidates[0]
            if len(candidates) > 1:
                dim_candidates = [c for c in candidates if c.startswith("dim_")]
                if dim_candidates:
                    return dim_candidates[0]
                return candidates[0]
    return None


async def get_table_info(state: AgentState, context: AgentContext) -> dict:
    question = state.rewritten_question
    embedding = await context.embedding.aembed_query(question)
    repo = ColumnQdrantRepository(context.qdrant_client)
    results = await repo.search(embedding=embedding, limit=20)

    all_vector_tables = []
    seen_names = set()
    for r in results:
        tn = r.get("table_name", "")
        tid = r.get("table_id", "")
        if tn and tn not in seen_names:
            all_vector_tables.append((tn, tid))
            seen_names.add(tn)

    logger.info(f"get_table_info: vector search found {len(all_vector_tables)} tables={[t[0] for t in all_vector_tables]}")

    core_tables = all_vector_tables[:MAX_VECTOR_TABLES]

    related_tables = await _find_related_tables(core_tables, context)

    priority_related = [(k, v) for k, v in related_tables.items() if _is_join_table(k)]
    fact_related = [(k, v) for k, v in related_tables.items() if _is_core_fact_table(k)]
    other_related = [(k, v) for k, v in related_tables.items() if not _is_join_table(k) and not _is_core_fact_table(k)]

    seen = {}
    for tn, tid in core_tables:
        seen[tn] = tid
    for tn, tid in fact_related + priority_related + other_related:
        if tn not in seen:
            seen[tn] = tid
        if len(seen) >= MAX_TOTAL_TABLES:
            break

    table_info = [{"name": name, "id": tid} for name, tid in seen.items()]
    logger.info(f"get_table_info: final tables={[t['name'] for t in table_info]}")
    return {"table_info": table_info}


async def _find_related_tables(
    core_tables: list[tuple[str, str]], context: AgentContext
) -> dict[str, str]:
    all_related: dict[str, str] = {}
    core_table_map = dict(core_tables)
    async with context.meta_session_factory() as session:
        repo = MetaMysqlRepository(session)
        all_tables = await repo.get_all_table_infos()
        all_table_map = {t.name: t.id for t in all_tables}
        id_to_name = {v: k for k, v in all_table_map.items()}
        all_table_names = set(all_table_map.keys())

        all_key_cols = await repo.get_all_key_columns()
        fk_list = [kc for kc in all_key_cols if kc.role == "foreign_key"]

        max_iterations = 3
        for iteration in range(max_iterations):
            known = {**core_table_map, **all_related}
            new_found: dict[str, str] = {}

            for kc in fk_list:
                desc = kc.description or ""
                col_name = kc.name
                fk_owner_id = kc.table_id
                fk_owner_name = id_to_name.get(fk_owner_id)

                if fk_owner_name not in known:
                    continue

                ref_from_desc = None
                for other_name in all_table_names:
                    if other_name in desc or f"{other_name}.id" in desc:
                        ref_from_desc = other_name
                        break

                ref_from_name = _infer_referenced_table(col_name, all_table_names)

                referenced_table = ref_from_desc or ref_from_name

                if referenced_table and referenced_table not in core_table_map and referenced_table not in all_related and referenced_table not in new_found:
                    new_found[referenced_table] = all_table_map[referenced_table]
                    logger.debug(f"  hop {iteration+1}: found {referenced_table} (referenced by {fk_owner_name}.{col_name})")

                if fk_owner_name and fk_owner_name not in core_table_map and fk_owner_name not in all_related and fk_owner_name not in new_found:
                    pass

            if not new_found:
                break
            all_related.update(new_found)
            logger.info(f"  hop {iteration+1}: found {len(new_found)} new tables: {list(new_found.keys())}")

    logger.info(f"_find_related_tables: found {len(all_related)} related tables: {list(all_related.keys())}")
    return all_related