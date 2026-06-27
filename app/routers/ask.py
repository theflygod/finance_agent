"""Ask API for natural language to SQL query with SSE streaming."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..response import ok
from ..services.query_service import query_service
from ..agent.state import AgentState

router = APIRouter(prefix="/api/v1", tags=["ask"])


class AskRequest(BaseModel):
    question: str = Field(description="自然语言问题，如'本月新增客户数是多少'")


@router.post("/ask", summary="自然语言问数(非流式)")
async def ask_endpoint(req: AskRequest) -> dict[str, Any]:
    result = await query_service.query(req.question)
    return ok(
        data={
            "question": result.get("question", ""),
            "sql": result.get("sql", ""),
            "data": result.get("sql_execution_result"),
            "answer": result.get("final_answer", ""),
            "error": result.get("sql_execution_error") or None,
        }
    )


@router.post("/ask/stream", summary="自然语言问数(SSE流式)")
async def ask_stream_endpoint(req: AskRequest) -> StreamingResponse:
    async def event_generator():
        async for node_name, node_state in query_service.query_stream(req.question):
            event_data = {"node": node_name, "state": {}}
            if isinstance(node_state, dict):
                for k, v in node_state.items():
                    try:
                        json.dumps(v, ensure_ascii=False, default=str)
                        event_data["state"][k] = v
                    except (TypeError, ValueError):
                        event_data["state"][k] = str(v)
            yield f"data: {json.dumps(event_data, ensure_ascii=False, default=str)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# 以下为前端兼容接口 /api/query
class FrontendQueryRequest(BaseModel):
    query: str = Field(description="用户自然语言问题")

frontend_router = APIRouter(prefix="/api", tags=["frontend-compat"])

_STAGE_MAP = {
    "get_table_info": "关联表检索中",
    "get_all_metadata": "字段/指标/维度检索中",
    "generate_sql": "SQL生成中",
    "review_sql": "SQL审查中",
    "execute_sql": "SQL执行中",
    "generate_answer": "结果整理中",
}

@frontend_router.post("/query", summary="前端SSE查询接口(兼容date-agent-frontend)")
async def frontend_query_endpoint(req: FrontendQueryRequest) -> StreamingResponse:
    """兼容前端Vue页面的SSE流式接口，格式为：
    - data: {"stage": "阶段描述"}\n\n
    - data: {"result": [...]} (最终结果表格)\n\n
    - data: {"error": "错误信息"}\n\n
    """
    from loguru import logger

    async def event_generator():
        logger.info(f"frontend query: {req.query}")

        def _safe_json(obj) -> str:
            return json.dumps(obj, ensure_ascii=False, default=str)

        def make_stage(node_name: str) -> str:
            stage_text = _STAGE_MAP.get(node_name, node_name)
            return f"data: {_safe_json({'stage': stage_text})}\n\n"

        graph = query_service._ensure_graph()
        initial_state = AgentState(question=req.query, rewritten_question=req.query, should_generate_sql=True)

        async for event in graph.astream(initial_state):
            for node_name, node_state in event.items():
                if node_name in _STAGE_MAP:
                    yield make_stage(node_name)

        final_state = await graph.ainvoke(initial_state)
        result = final_state.get("sql_execution_result")
        error = final_state.get("sql_execution_error")

        if error:
            yield f"data: {_safe_json({'error': error})}\n\n"
        elif result is not None:
            yield f"data: {_safe_json({'result': result})}\n\n"
        else:
            yield f"data: {_safe_json({'error': '未获取到查询结果'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )