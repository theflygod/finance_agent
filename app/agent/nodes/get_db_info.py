"""Node: get DB info (dialect, version)."""

from __future__ import annotations

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.repository.mysql.dw_mysql_repository import DwMysqlRepository


async def get_db_info(state: AgentState, context: AgentContext) -> dict:
    async with context.dw_session_factory() as session:
        repo = DwMysqlRepository(session)
        db_info = await repo.get_db_info()
    return {"db_info": db_info}