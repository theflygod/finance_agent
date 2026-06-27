"""Node: retrieve metric info from Qdrant vector search."""

from __future__ import annotations

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.repository.qdrant.metric_qdrant_repository import MetricQdrantRepository


async def get_metric_info(state: AgentState, context: AgentContext) -> dict:
    question = state.rewritten_question
    embedding = await context.embedding.aembed_query(question)
    repo = MetricQdrantRepository(context.qdrant_client)
    results = await repo.search(embedding=embedding, limit=10)
    return {"metric_info": results}