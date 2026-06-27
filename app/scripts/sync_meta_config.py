"""Sync meta_config.yaml with actual database schema.

Reads actual column names from MySQL and merges with existing meta_config.yaml
descriptions/aliases. Outputs a new meta_config.yaml that has correct column names
but preserves human-written descriptions and aliases where possible.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pymysql
from omegaconf import OmegaConf

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

DB_HOST = "192.168.10.150"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "123321"
DB_NAME = "finance"

ROLE_OVERRIDES = {
    "id": "primary_key",
    "contract_no": "dimension",
    "loan_no": "dimension",
    "account_no": "dimension",
    "card_no": "dimension",
    "case_no": "dimension",
    "order_no": "dimension",
    "ticket_no": "dimension",
    "report_no": "dimension",
    "rule_code": "dimension",
    "strategy_code": "dimension",
    "product_code": "dimension",
    "service_code": "dimension",
    "event_no": "dimension",
    "income_no": "dimension",
    "ledger_no": "dimension",
    "transaction_no": "dimension",
    "disposal_no": "dimension",
    "action_no": "dimension",
    "blacklist_no": "dimension",
    "review_no": "dimension",
    "instance_no": "dimension",
    "task_no": "dimension",
    "notice_no": "dimension",
    "feedback_no": "dimension",
    "channel_txn_no": "dimension",
    "biz_order_no": "dimension",
}

DESCRIPTION_MAP = {
    "id": "主键ID",
    "contract_no": "合同编号",
    "loan_no": "借据号/贷款编号",
    "application_id": "申请ID",
    "customer_id": "客户ID",
    "product_id": "产品ID",
    "branch_id": "机构ID",
    "channel_id": "渠道ID",
    "account_id": "账户ID",
    "contract_id": "合同ID",
    "transaction_id": "交易ID",
    "currency_code": "币种代码",
    "principal_amount": "本金金额",
    "disbursed_principal_amount": "已放款本金金额",
    "undisbursed_principal_amount": "未放款本金金额",
    "written_off_principal_amount": "核销本金金额",
    "restructured_principal_amount": "重组本金金额",
    "outstanding_principal_amount": "贷款余额/未偿本金",
    "annual_interest_rate": "年利率",
    "term_months": "期限(月)",
    "repayment_method": "还款方式",
    "contract_status": "合同状态",
    "signed_at": "签约时间",
    "disbursed_at": "放款时间",
    "settled_at": "结清时间",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "apply_amount": "申请金额",
    "apply_term": "申请期限(月)",
    "application_status": "申请状态",
    "submitted_at": "提交时间",
    "disbursement_amount": "放款金额",
    "disbursement_status": "放款状态",
    "repayment_amount": "还款金额",
    "principal_paid_amount": "已还本金",
    "interest_paid_amount": "已还利息",
    "fee_paid_amount": "已还费用",
    "penalty_paid_amount": "已还罚息",
    "repayment_status": "还款状态",
    "repaid_at": "还款时间",
    "balance_amount": "账户余额",
    "frozen_amount": "冻结金额",
    "available_amount": "可用余额",
    "account_type": "账户类型",
    "account_status": "账户状态",
    "opened_at": "开户时间",
    "closed_at": "关闭时间",
    "due_amount": "应还金额",
    "schedule_status": "计划状态",
    "due_date": "到期日期",
    "period_no": "期数",
    "interest_amount": "利息金额",
    "fee_amount": "费用金额",
    "total_amount": "总金额",
    "risk_level_id": "风险等级ID",
    "risk_score": "风险评分",
    "event_type": "事件类型",
    "event_status": "事件状态",
    "decision_action": "决策动作",
    "max_amount": "最高金额",
    "min_amount": "最低金额",
    "annual_rate": "年利率",
    "loan_type": "贷款类型",
    "product_status": "产品状态",
    "product_name": "产品名称",
    "customer_name": "客户名称",
    "customer_type": "客户类型",
    "customer_status": "客户状态",
    "identity_type": "证件类型",
    "identity_no": "证件号码",
    "mobile": "手机号",
    "email": "邮箱",
    "blacklist_reason": "黑名单原因",
    "blacklist_status": "黑名单状态",
    "collection_stage": "催收阶段",
    "case_status": "案件状态",
    "case_amount": "案件金额",
    "collateral_status": "抵质押状态",
    "asset_type": "资产类型",
    "asset_name": "资产名称",
    "appraised_value_amount": "评估价值",
    "pledge_rate": "质押率",
    "secured_amount": "担保金额",
    "credit_limit": "授信额度",
    "used_amount": "已用额度",
    "available_limit": "可用额度",
    "limit_status": "额度状态",
    "order_type": "订单类型",
    "order_status": "订单状态",
    "order_amount": "订单金额",
    "order_share": "订单份额",
    "confirmed_amount": "确认金额",
    "confirmed_share": "确认份额",
    "holding_share": "持有份额",
    "available_share": "可用份额",
    "frozen_share": "冻结份额",
    "cost_amount": "成本金额",
    "market_value_amount": "市值金额",
    "accumulated_income_amount": "累计收益金额",
    "unit_nav": "单位净值",
    "accumulated_nav": "累计净值",
    "nav_date": "净值日期",
    "income_amount": "收益金额",
    "income_type": "收益类型",
    "income_date": "收益日期",
    "transaction_amount": "交易金额",
    "transaction_type": "交易类型",
    "transaction_status": "交易状态",
    "transaction_at": "交易时间",
    "ticket_type": "工单类型",
    "ticket_status": "工单状态",
    "ticket_title": "工单标题",
    "ticket_content": "工单内容",
    "handle_result": "处理结果",
    "satisfaction_score": "满意度评分",
    "feedback_content": "反馈内容",
    "confirm_status": "确认状态",
    "metric_code": "指标编码",
    "metric_name": "指标名称",
    "metric_value": "指标值",
    "stat_date": "统计日期",
    "stat_domain": "统计域",
    "metric_type": "指标类型",
    "metric_unit": "指标单位",
}

ALIAS_MAP = {
    "outstanding_principal_amount": ["贷款余额", "未偿本金", "剩余本金"],
    "principal_amount": ["本金金额", "本金"],
    "disbursed_principal_amount": ["已放款本金", "已放款金额"],
    "undisbursed_principal_amount": ["未放款本金", "未放款金额"],
    "contract_status": ["合同状态", "贷款状态"],
    "annual_interest_rate": ["年利率", "利率"],
    "term_months": ["期限", "贷款期限", "合同期限"],
    "repayment_method": ["还款方式"],
    "disbursement_amount": ["放款金额", "放款额"],
    "apply_amount": ["申请金额", "申请额"],
    "repayment_amount": ["还款金额", "还款额"],
    "balance_amount": ["余额", "账户余额"],
    "credit_limit": ["授信额度", "额度"],
    "used_amount": ["已用额度", "已用额"],
    "available_limit": ["可用额度", "可用额"],
    "transaction_amount": ["交易金额", "交易额"],
    "order_amount": ["订单金额", "订单额"],
    "customer_name": ["客户名称", "客户名"],
    "contract_no": ["合同编号", "借据号"],
    "loan_no": ["贷款编号", "借据号"],
}


def infer_role(col_name: str, col_type: str, is_pk: bool) -> str:
    if is_pk:
        return "primary_key"
    if col_name in ROLE_OVERRIDES:
        return ROLE_OVERRIDES[col_name]
    if col_name.endswith("_id"):
        return "foreign_key"
    if any(kw in col_name for kw in ("amount", "balance", "rate", "score", "count", "share", "fee", "value", "limit", "ratio", "price")):
        return "measure"
    return "dimension"


def main():
    conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]

    existing_config = OmegaConf.load(ROOT_DIR / "conf" / "meta_config.yaml")
    existing_tables = {}
    if hasattr(existing_config, "tables"):
        for t in existing_config.tables:
            existing_tables[t.name] = {}
            if hasattr(t, "columns"):
                for c in t.columns:
                    existing_tables[t.name][c.name] = c

    existing_metrics = []
    if hasattr(existing_config, "metrics"):
        existing_metrics = list(existing_config.metrics)

    lines = ["tables:"]
    for t_name in sorted(tables):
        cursor.execute(f"DESCRIBE `{t_name}`")
        cols = cursor.fetchall()

        existing_t = existing_tables.get(t_name, {})
        t_desc = ""
        if t_name in existing_tables:
            t_desc = getattr(existing_config.tables, t_name, "")
        for et in (existing_config.tables if hasattr(existing_config, "tables") else []):
            if et.name == t_name:
                t_desc = getattr(et, "description", t_name)
                break

        lines.append(f"  - name: {t_name}")
        lines.append(f"    role: fact")
        lines.append(f'    description: "{t_desc or t_name}表"')
        lines.append(f"    columns:")

        for col in cols:
            name, col_type, nullable, key, default, extra = col
            is_pk = key == "PRI"
            role = infer_role(name, col_type, is_pk)

            desc = DESCRIPTION_MAP.get(name, name)
            alias = ALIAS_MAP.get(name, [])

            if name in existing_t:
                ec = existing_t[name]
                if hasattr(ec, "description") and ec.description and ec.description != name:
                    desc = ec.description
                if hasattr(ec, "alias") and ec.alias:
                    alias = list(ec.alias)

            sync_val = "true" if role == "dimension" and not name.endswith("_id") and name not in ("id", "created_at", "updated_at") else "false"

            lines.append(f"      - name: {name}")
            lines.append(f"        role: {role}")
            lines.append(f'        description: "{desc}"')
            alias_str = ", ".join(f'"{a}"' for a in alias)
            lines.append(f"        alias: [{alias_str}]")
            lines.append(f"        sync: {sync_val}")

    if existing_metrics:
        lines.append("")
        lines.append("metrics:")
        for m in existing_metrics:
            lines.append(f"  - name: {m.name}")
            lines.append(f'    description: "{getattr(m, "description", "")}"')
            if hasattr(m, "alias") and m.alias:
                alias_str = ", ".join(f'"{a}"' for a in m.alias)
                lines.append(f"    alias: [{alias_str}]")
            if hasattr(m, "relevant_columns") and m.relevant_columns:
                cols_str = ", ".join(f'"{c}"' for c in m.relevant_columns)
                lines.append(f"    relevant_columns: [{cols_str}]")

    output_path = ROOT_DIR / "conf" / "meta_config.yaml"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {output_path}")
    print(f"Tables: {len(tables)}, Metrics: {len(existing_metrics)}")

    conn.close()


if __name__ == "__main__":
    main()