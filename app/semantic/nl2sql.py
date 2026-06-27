"""NL2SQL engine powered by Qwen LLM."""

from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from ..config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from ..database import fetch_all
from .metadata import SYNONYM_MAP, build_schema_prompt

SYSTEM_PROMPT = """你是一个金融业务数据分析师，擅长将自然语言问题转换为准确的 SQL 查询。

## 规则
1. 只能生成 SELECT 查询，禁止生成 INSERT/UPDATE/DELETE/DROP 等写操作。
2. 必须使用上面提供的表名和字段名，不要编造不存在的表或字段。
3. 金额类字段使用 decimal 类型，注意不要丢失精度。
4. 时间过滤使用标准 SQL 日期函数，如 DATE()、YEAR()、MONTH()、CURDATE()、DATE_SUB() 等。
5. 统计客户数用 COUNT(DISTINCT customer.id)，统计账户数用 COUNT(DISTINCT bank_account.id)。
6. 统计金额用 SUM()，注意配合对应的状态过滤条件。
7. "本月"指当前月份，"最近30天"用 DATE_SUB(CURDATE(), INTERVAL 30 DAY)。
8. 按机构维度分析时 JOIN dim_branch 表，按渠道维度分析时 JOIN dim_channel 表。
9. 枚举值必须使用英文编码，如 active/normal/success 等，不要用中文。
10. 输出必须是纯 SQL，不要包含 markdown 代码块标记（如 ```sql），不要包含注释和解释。

## 同义词映射
{synonym_section}

{schema_section}
"""

SYNONYM_SECTION_LINES: list[str] = []
for main_term, synonyms in SYNONYM_MAP.items():
    SYNONYM_SECTION_LINES.append(f"- 「{main_term}」同义于：{'、'.join(synonyms)}")
SYNONYM_TEXT = "\n".join(SYNONYM_SECTION_LINES)

FULL_SYSTEM_PROMPT = SYSTEM_PROMPT.format(
    synonym_section=SYNONYM_TEXT,
    schema_section=build_schema_prompt(),
)


def _create_client() -> OpenAI:
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)


def generate_sql(question: str) -> dict[str, Any]:
    client = _create_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": FULL_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0.1,
        max_tokens=1024,
    )
    raw_sql = response.choices[0].message.content.strip()
    sql = _clean_sql(raw_sql)
    return {
        "question": question,
        "raw_sql": raw_sql,
        "sql": sql,
    }


def execute_sql(sql: str) -> list[dict[str, Any]]:
    try:
        rows = fetch_all(sql)
        return rows
    except Exception as e:
        return [{"error": str(e)}]


def _clean_sql(raw: str) -> str:
    sql = raw.strip()
    sql = re.sub(r"^```sql\s*", "", sql)
    sql = re.sub(r"^```\s*", "", sql)
    sql = re.sub(r"\s*```\s*$", "", sql)
    sql = sql.strip()
    if sql.endswith(";"):
        sql = sql[:-1].strip()
    return sql


def ask(question: str) -> dict[str, Any]:
    gen = generate_sql(question)
    sql = gen["sql"]
    rows = execute_sql(sql)
    has_error = len(rows) == 1 and "error" in rows[0]
    return {
        "question": question,
        "sql": sql,
        "data": rows if not has_error else None,
        "error": rows[0]["error"] if has_error else None,
    }