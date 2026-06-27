"""Node: generate SQL using LLM with retrieved context."""

from __future__ import annotations

import json

from langchain_core.messages import HumanMessage

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.prompt.prompt_loader import load_prompt


async def generate_sql(state: AgentState, context: AgentContext) -> dict:
    prompt_template = load_prompt("generate_sql")
    prompt = prompt_template.format(
        db_info=json.dumps(state.db_info, ensure_ascii=False),
        table_info=json.dumps(state.table_info, ensure_ascii=False),
        column_info=json.dumps(state.column_info, ensure_ascii=False),
        metric_info=json.dumps(state.metric_info, ensure_ascii=False),
        value_info=json.dumps(state.value_info, ensure_ascii=False),
        key_column_info=json.dumps(state.key_column_info, ensure_ascii=False),
        question=state.rewritten_question,
    )
    response = await context.llm.ainvoke([HumanMessage(content=prompt)])
    sql = response.content.strip()
    if sql.startswith("```sql"):
        sql = sql[6:]
    if sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]
    sql = sql.strip()
    return {"sql": sql}