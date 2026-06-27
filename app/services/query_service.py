"""Query service: orchestrates the NL2SQL agent."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from loguru import logger

from app.agent.context import AgentContext
from app.agent.graph import build_graph
from app.agent.llm import create_llm
from app.agent.state import AgentState
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager


class QueryService:

    def __init__(self):
        self._context: AgentContext | None = None
        self._compiled_graph = None

    def _ensure_context(self) -> AgentContext:
        if self._context is None:
            self._context = AgentContext(
                llm=create_llm(),
                embedding=embedding_client_manager.client,
                qdrant_client=qdrant_client_manager.client,
                es_client=es_client_manager.client,
                dw_session_factory=dw_mysql_client_manager.session_factory,
                meta_session_factory=meta_mysql_client_manager.session_factory,
            )
        return self._context

    def _ensure_graph(self):
        if self._compiled_graph is None:
            context = self._ensure_context()
            graph = build_graph(context)
            self._compiled_graph = graph.compile()
        return self._compiled_graph

    async def query(self, question: str) -> AgentState:
        graph = self._ensure_graph()
        initial_state = AgentState(question=question)
        result = await graph.ainvoke(initial_state)
        return result

    async def query_stream(self, question: str):
        graph = self._ensure_graph()
        initial_state = AgentState(question=question)
        async for event in graph.astream(initial_state):
            for node_name, node_state in event.items():
                yield node_name, node_state


query_service = QueryService()