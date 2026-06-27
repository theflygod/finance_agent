"""LLM factory: create LangChain ChatOpenAI for Alibaba Cloud DashScope."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from app.conf.app_config import app_config


def create_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=app_config.llm.model_name,
        api_key=app_config.llm.api_key,
        base_url=app_config.llm.base_url,
        temperature=0,
    )