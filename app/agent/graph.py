"""LangGraph NL2SQL agent graph definition."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agent.context import AgentContext
from app.agent.nodes.execute_sql import execute_sql
from app.agent.nodes.generate_answer import generate_answer
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.get_all_metadata import get_all_metadata
from app.agent.nodes.get_db_info import get_db_info
from app.agent.nodes.get_table_info import get_table_info
from app.agent.nodes.review_sql import review_sql
from app.agent.nodes.rewrite_sql import rewrite_sql
from app.agent.state import AgentState


def _review_result(state: AgentState) -> str:
    if state.sql_review_passed:
        return "execute_sql"
    if state.rewrite_count >= state.max_rewrite_count:
        return "execute_sql"
    return "rewrite_sql"


def _execution_result(state: AgentState) -> str:
    if state.sql_execution_passed:
        return "generate_answer"
    if state.rewrite_count >= state.max_rewrite_count:
        return "generate_answer"
    return "rewrite_sql"


def _make_node(func, context):
    async def _node(state):
        return await func(state, context)
    return _node


def build_graph(context: AgentContext) -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("get_db_info", _make_node(get_db_info, context))
    graph.add_node("get_table_info", _make_node(get_table_info, context))
    graph.add_node("get_all_metadata", _make_node(get_all_metadata, context))
    graph.add_node("generate_sql", _make_node(generate_sql, context))
    graph.add_node("review_sql", _make_node(review_sql, context))
    graph.add_node("rewrite_sql", _make_node(rewrite_sql, context))
    graph.add_node("execute_sql", _make_node(execute_sql, context))
    graph.add_node("generate_answer", _make_node(generate_answer, context))

    graph.set_entry_point("get_db_info")

    graph.add_edge("get_db_info", "get_table_info")
    graph.add_edge("get_table_info", "get_all_metadata")
    graph.add_edge("get_all_metadata", "generate_sql")
    graph.add_edge("generate_sql", "review_sql")
    graph.add_conditional_edges("review_sql", _review_result)
    graph.add_edge("rewrite_sql", "review_sql")
    graph.add_conditional_edges("execute_sql", _execution_result)
    graph.add_edge("generate_answer", END)

    return graph