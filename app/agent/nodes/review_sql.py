"""Node: review generated SQL - programmatic checks + LLM review."""

from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage

from app.agent.context import AgentContext
from app.agent.state import AgentState
from app.prompt.prompt_loader import load_prompt


def _extract_table_names(sql: str) -> set[str]:
    patterns = [
        r'\bFROM\s+(\w+)',
        r'\bJOIN\s+(\w+)',
        r'\bINTO\s+(\w+)',
        r'\bUPDATE\s+(\w+)',
    ]
    names = set()
    for pat in patterns:
        for m in re.finditer(pat, sql, re.IGNORECASE):
            names.add(m.group(1).lower())
    return names


def _extract_column_names(sql: str, table_names: set[str] = None) -> set[str]:
    table_names = table_names or set()
    patterns = [
        r'\bSELECT\s+(.*?)\s+FROM',
        r'\bWHERE\s+(.*?)(?:\s+GROUP|\s+ORDER|\s+LIMIT|\s*$)',
        r'\bON\s+(\w+)\.(\w+)\s*=\s*\w+\.\w+',
        r'\bGROUP\s+BY\s+(.*?)(?:\s+ORDER|\s+LIMIT|\s*$)',
        r'\bORDER\s+BY\s+(.*?)(?:\s+LIMIT|\s*$)',
    ]
    sql_keywords = {
        'select', 'from', 'where', 'and', 'or', 'not', 'in', 'like',
        'between', 'is', 'null', 'as', 'on', 'sum', 'count', 'avg',
        'max', 'min', 'group', 'order', 'by', 'asc', 'desc', 'limit',
        'distinct', 'having', 'join', 'inner', 'left', 'right', 'outer',
        'case', 'when', 'then', 'else', 'end', 'cast', 'coalesce', 'if',
        'ifnull', 'nullif', 'round', 'abs', 'concat', 'substring', 'date',
        'year', 'month', 'day', 'hour', 'minute', 'second', 'curdate',
        'now', 'date_format', 'datediff', 'timestampdiff', 'exists',
        'any', 'all', 'some', 'union', 'intersect', 'except', 'with',
        'into', 'values', 'set', 'true', 'false', 'div', 'mod', 'xor',
        'interval', 'date_sub', 'date_add', 'date_trunc', 'extract',
        'over', 'partition', 'row_number', 'rank', 'dense_rank', 'lag', 'lead',
        'first_value', 'last_value', 'nth_value', 'ntile', 'rows', 'range',
        'unbounded', 'preceding', 'following', 'current', 'row', 'window',
        'created', 'processing', 'success', 'failed', 'reversed', 'active',
        'pending', 'matched', 'mismatched', 'adjusted', 'not_required',
        'cancelled', 'closed', 'expired', 'suspended', 'frozen', 'normal',
        'completed', 'transfer', 'consume', 'deposit', 'withdraw', 'refund',
        'cancel', 'reversal', 'adjustment', 't', 'n',
    }
    names = set()
    for pat in patterns:
        match = re.search(pat, sql, re.IGNORECASE | re.DOTALL)
        if match:
            part = match.group(1)
            for token in re.findall(r'(\w+)\.(\w+)', part):
                col_name = token[1].lower()
                if col_name not in sql_keywords:
                    names.add(col_name)
            for token in re.findall(r'(?<!\.)\b([a-zA-Z_]\w*)\b', part):
                token_lower = token.lower()
                if token_lower not in sql_keywords and token_lower not in table_names:
                    names.add(token_lower)
    return names


def _programmatic_review(sql: str, allowed_tables: set[str], allowed_columns: set[str] = None) -> list[str]:
    issues = []
    sql_lower = sql.lower().strip()
    if not sql_lower.startswith("select"):
        issues.append("SQL不是SELECT语句")
    if re.search(r'\b(drop|delete|insert|update|alter|truncate|create)\b', sql_lower[6:] if len(sql_lower) > 6 else ""):
        issues.append("SQL包含危险操作(DROP/DELETE/INSERT/UPDATE等)")
    if "cross join" in sql_lower:
        issues.append("使用了CROSS JOIN，可能导致笛卡尔积，请使用JOIN ON")
    used_tables = _extract_table_names(sql)
    disallowed = used_tables - allowed_tables
    if disallowed:
        issues.append(f"SQL使用了未提供的表: {disallowed}")
    join_count = len(re.findall(r'\bJOIN\b', sql, re.IGNORECASE))
    from_tables = len(re.findall(r'\bFROM\b', sql, re.IGNORECASE))
    if join_count + from_tables > 1 and " ON " not in sql.upper():
        issues.append("多表查询但缺少JOIN ON条件，可能导致笛卡尔积")
    if allowed_columns:
        used_columns = _extract_column_names(sql, allowed_tables)
        disallowed_cols = used_columns - allowed_columns
        if disallowed_cols:
            issues.append(f"SQL使用了未提供的列: {disallowed_cols}")
    return issues


async def review_sql(state: AgentState, context: AgentContext) -> dict:
    allowed_tables = {t.get("name", "").lower() for t in state.table_info}
    allowed_columns = {c.get("name", "").lower() for c in state.column_info}

    prog_issues = _programmatic_review(state.sql, allowed_tables, allowed_columns)
    if prog_issues:
        result = "程序化审查失败: " + "; ".join(prog_issues)
        logger_msg = f"review_sql: programmatic check failed: {prog_issues}"
        from loguru import logger
        logger.warning(logger_msg)
        return {"sql_review_result": result, "sql_review_passed": False}

    prompt_template = load_prompt("review_sql")
    prompt = prompt_template.format(
        db_info=json.dumps(state.db_info, ensure_ascii=False),
        table_info=json.dumps(state.table_info, ensure_ascii=False),
        column_info=json.dumps(state.column_info, ensure_ascii=False),
        sql=state.sql,
    )
    response = await context.llm.ainvoke([HumanMessage(content=prompt)])
    result = response.content.strip()
    passed = result.lower() == "passed"
    return {"sql_review_result": result, "sql_review_passed": passed}