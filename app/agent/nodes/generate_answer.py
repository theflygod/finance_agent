"""Node: generate final answer from SQL execution result."""

from __future__ import annotations

import json

from langchain_core.messages import HumanMessage

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.prompt.prompt_loader import load_prompt


async def generate_answer(state: AgentState, context: AgentContext) -> dict:
    prompt_template = load_prompt("generate_answer")
    prompt = prompt_template.format(
        question=state.rewritten_question,
        sql=state.sql,
        result=json.dumps(state.sql_execution_result, ensure_ascii=False, default=str),
    )
    response = await context.llm.ainvoke([HumanMessage(content=prompt)])
    return {"final_answer": response.content.strip()}