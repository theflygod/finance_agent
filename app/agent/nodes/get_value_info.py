"""Node: retrieve dimension value info from Elasticsearch."""

from __future__ import annotations

import jieba

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.repository.es.value_es_repository import ValueEsRepository


async def get_value_info(state: AgentState, context: AgentContext) -> dict:
    question = state.rewritten_question
    words = list(jieba.cut(question))
    repo = ValueEsRepository(context.es_client)
    all_results = []
    for word in words:
        if len(word) < 2:
            continue
        results = await repo.search(keyword=word, limit=10)
        all_results.extend(results)
    unique = []
    seen = set()
    for r in all_results:
        key = r.get("id", "")
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return {"value_info": unique}