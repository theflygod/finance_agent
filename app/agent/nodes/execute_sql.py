"""Node: execute SQL against the data warehouse."""

from __future__ import annotations

from loguru import logger

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.repository.mysql.dw_mysql_repository import DwMysqlRepository


async def execute_sql(state: AgentState, context: AgentContext) -> dict:
    sql = state.sql
    try:
        async with context.dw_session_factory() as session:
            repo = DwMysqlRepository(session)
            result = await repo.execute_sql(sql)
        return {"sql_execution_result": result, "sql_execution_error": "", "sql_execution_passed": True}
    except Exception as e:
        logger.warning(f"SQL execution failed: {e}")
        return {"sql_execution_result": [], "sql_execution_error": str(e), "sql_execution_passed": False}