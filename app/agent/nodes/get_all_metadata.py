"""Node: retrieve all metadata in parallel (column/metric/value/key_column info)."""

from __future__ import annotations

import asyncio

from loguru import logger

from app.agent.context import AgentContext
from app.agent.nodes.get_column_info import get_column_info
from app.agent.nodes.get_key_column_info import get_key_column_info
from app.agent.nodes.get_metric_info import get_metric_info
from app.agent.nodes.get_value_info import get_value_info
from app.agent.state import AgentState


async def get_all_metadata(state: AgentState, context: AgentContext) -> dict:
    logger.info("get_all_metadata: running 4 metadata retrievals in parallel")
    results = await asyncio.gather(
        get_column_info(state, context),
        get_metric_info(state, context),
        get_value_info(state, context),
        get_key_column_info(state, context),
    )
    combined = {}
    for r in results:
        combined.update(r)
    logger.info(
        f"get_all_metadata: done - columns={len(combined.get('column_info', []))}, "
        f"metrics={len(combined.get('metric_info', []))}, "
        f"values={len(combined.get('value_info', []))}, "
        f"keys={len(combined.get('key_column_info', []))}"
    )
    return combined