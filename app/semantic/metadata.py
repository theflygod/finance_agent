"""Financial business semantic metadata for NL2SQL."""

from __future__ import annotations

TABLE_METADATA: dict[str, dict[str, str]] = {
    "dim_branch": {
        "description": "银行机构维表，维护总行、分行、支行和营业网点",
        "columns": {
            "id": "机构ID，主键",
            "parent_id": "父机构ID，总行为空",
            "branch_code": "机构编码，业务唯一标识",
            "branch_name": "机构名称",
            "branch_level": "机构层级：head_office总行/branch分行/sub_branch支行/outlet营业网点",
            "province": "所在省份",
            "city": "所在城市",
            "address": "机构地址",
            "service_phone": "客服电话",
            "branch_status": "机构状态：active启用/suspended暂停/closed关闭",
            "opened_at": "开业时间",
            "closed_at": "关闭时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "dim_channel": {
        "description": "业务渠道维表，维护手机银行、网上银行、柜面等渠道",
        "columns": {
            "id": "渠道ID，主键",
            "channel_code": "渠道编码：MOBILE_BANK手机银行/ONLINE_BANK网上银行/COUNTER柜面/OPEN_API开放银行/PARTNER_APP合作方/BATCH_JOB批处理",
            "channel_name": "渠道名称",
            "channel_type": "渠道类型：mobile_bank/online_bank/counter/open_api/partner/batch",
            "channel_status": "渠道状态：active启用/suspended暂停/offline下线",
            "yn": "是否启用，1启用0停用",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "dim_currency": {
        "description": "币种维表，维护CNY人民币等币种",
        "columns": {
            "id": "币种ID",
            "currency_code": "币种代码，如CNY/USD",
            "currency_name": "币种名称",
            "symbol": "币种符号",
            "precision_scale": "金额精度位数",
            "yn": "是否启用",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "dim_risk_level": {
        "description": "风险等级维表，统一定义客户、产品和事件风险等级",
        "columns": {
            "id": "风险等级ID",
            "risk_level_code": "风险等级编码，如C1保守型/C2稳健型/C3平衡型/C4成长型/C5进取型",
            "risk_level_name": "风险等级名称",
            "risk_level_type": "等级类型：customer客户/product产品/event事件",
            "risk_score_min": "等级分数下限",
            "risk_score_max": "等级分数上限",
            "sort_no": "排序号，越大风险越高",
            "yn": "是否启用",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "dim_employee": {
        "description": "员工主数据维表，维护员工编号、姓名、所属机构、岗位角色",
        "columns": {
            "id": "员工ID",
            "employee_no": "员工编号，业务唯一标识",
            "employee_name": "员工姓名",
            "branch_id": "所属机构ID，关联dim_branch.id",
            "employee_role": "员工角色：relationship_manager客户经理/loan_approver信贷审批员/risk_officer风控员/collector催收员/operator运营/customer_service客服",
            "permission_codes": "员工权限编码集合(JSON)",
            "mobile": "手机号",
            "email": "邮箱",
            "employee_status": "员工状态：active在职/suspended停用/resigned离职",
            "joined_at": "入职时间",
            "resigned_at": "离职时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "dim_product_category": {
        "description": "产品分类维表，定义账户、贷款、理财和服务产品分类",
        "columns": {
            "id": "分类ID",
            "parent_id": "父分类ID，顶级为空",
            "category_code": "分类编码",
            "category_name": "分类名称",
            "category_type": "分类类型：account账户/loan贷款/wealth理财/service服务",
            "category_level": "分类层级",
            "sort_no": "排序号",
            "yn": "是否启用",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "customer": {
        "description": "客户主表，统一存储个人客户和企业客户的客户号、类型和生命周期状态",
        "columns": {
            "id": "客户ID，主键",
            "customer_no": "客户号，业务唯一标识",
            "customer_type": "客户类型：personal个人/enterprise企业",
            "customer_name": "客户名称",
            "branch_id": "归属机构ID，关联dim_branch.id",
            "register_channel_id": "注册渠道ID，关联dim_channel.id",
            "risk_level_id": "客户风险等级ID，关联dim_risk_level.id",
            "customer_status": "客户状态：pending_kyc待实名/active正常/restricted限制/frozen冻结/closed销户",
            "opened_at": "开户时间",
            "closed_at": "销户时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "customer_identity": {
        "description": "客户实名信息表，维护证件、姓名、实名状态和认证结果",
        "columns": {
            "id": "实名ID",
            "customer_id": "客户ID，关联customer.id",
            "identity_type": "证件类型：id_card身份证/passport护照/business_license营业执照",
            "identity_no": "证件号码",
            "identity_name": "证件姓名",
            "identity_status": "实名状态：pending待认证/verified已认证/rejected认证失败",
            "verified_at": "认证时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "customer_kyc": {
        "description": "客户KYC表，维护职业、收入、资金来源、行业和合规状态",
        "columns": {
            "id": "KYC ID",
            "customer_id": "客户ID，关联customer.id",
            "occupation": "职业",
            "monthly_income": "月收入",
            "income_source": "收入来源",
            "industry": "行业",
            "kyc_status": "KYC状态：pending待提交/submitted已提交/valid有效/expired过期",
            "submitted_at": "提交时间",
            "verified_at": "验证时间",
            "expire_at": "过期时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "customer_risk_assessment": {
        "description": "客户风险测评表，维护理财风险承受能力和测评结果",
        "columns": {
            "id": "测评ID",
            "customer_id": "客户ID，关联customer.id",
            "risk_level_id": "测评风险等级ID，关联dim_risk_level.id",
            "assessment_score": "测评分数",
            "assessment_status": "测评状态：pending待测评/completed已完成/expired已过期",
            "assessed_at": "测评时间",
            "expire_at": "过期时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "customer_tag": {
        "description": "客户标签表，维护客户分群、营销标签、风险标签",
        "columns": {
            "id": "标签ID",
            "tag_code": "标签编码",
            "tag_name": "标签名称",
            "tag_type": "标签类型：segment分群/marketing营销/risk风险/operation运营",
            "tag_value": "标签值",
            "yn": "是否启用",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "customer_tag_rel": {
        "description": "客户标签关系表，维护客户和标签的多对多关系",
        "columns": {
            "id": "关系ID",
            "customer_id": "客户ID，关联customer.id",
            "tag_id": "标签ID，关联customer_tag.id",
            "created_at": "创建时间",
        },
    },
    "bank_account": {
        "description": "银行账户表，维护账户类型、余额、冻结金额和账户状态",
        "columns": {
            "id": "账户ID",
            "account_no": "账号，业务唯一标识",
            "customer_id": "客户ID，关联customer.id",
            "product_id": "账户产品ID，关联account_product.id",
            "branch_id": "开户机构ID，关联dim_branch.id",
            "currency_code": "币种代码，关联dim_currency.currency_code",
            "account_type": "账户类型：demand_deposit活期/settlement结算/loan_repayment贷款还款/wealth_settlement理财结算",
            "balance": "账户余额",
            "frozen_amount": "冻结金额",
            "account_status": "账户状态：active正常/frozen冻结/closed关闭",
            "opened_at": "开户时间",
            "closed_at": "销户时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "account_transaction": {
        "description": "账户交易流水表，记录转账、消费、充值、提现等交易",
        "columns": {
            "id": "交易ID",
            "transaction_no": "交易流水号",
            "account_id": "账户ID，关联bank_account.id",
            "customer_id": "客户ID，关联customer.id",
            "channel_id": "交易渠道ID，关联dim_channel.id",
            "transaction_type": "交易类型：transfer转账/consumption消费/recharge充值/withdrawal提现/refund退款/reversal冲正",
            "amount": "交易金额",
            "currency_code": "币种代码",
            "transaction_status": "交易状态：success成功/failed失败/pending处理中",
            "transaction_date": "交易日期",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "channel_transaction": {
        "description": "渠道交易流水表，记录各渠道的交易统计",
        "columns": {
            "id": "渠道交易ID",
            "channel_id": "渠道ID，关联dim_channel.id",
            "transaction_date": "交易日期",
            "transaction_count": "交易笔数",
            "transaction_amount": "交易金额",
            "currency_code": "币种代码",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "wealth_product": {
        "description": "理财产品表，维护产品名称、风险等级、预期收益率和销售状态",
        "columns": {
            "id": "理财产品ID",
            "product_code": "产品编码",
            "product_name": "产品名称",
            "category_id": "产品分类ID，关联dim_product_category.id",
            "currency_code": "币种代码",
            "risk_level_id": "产品风险等级ID，关联dim_risk_level.id",
            "product_type": "产品类型：fixed_term定期/open_ended开放式/structured结构性",
            "operation_mode": "运作方式：net_value净值型/yield_rate收益型",
            "min_purchase_amount": "最低申购金额",
            "increment_amount": "递增金额",
            "expected_yield_rate": "预期收益率",
            "nav_based_flag": "是否净值型：1是0否",
            "sale_start_at": "销售开始时间",
            "sale_end_at": "销售结束时间",
            "value_date_rule": "起息规则",
            "redeem_rule": "赎回规则",
            "product_status": "产品状态：draft草稿/active启用/paused暂停/offline下线",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "wealth_order": {
        "description": "理财订单表，维护申购和赎回订单",
        "columns": {
            "id": "订单ID",
            "order_no": "订单编号",
            "customer_id": "客户ID，关联customer.id",
            "account_id": "账户ID，关联bank_account.id",
            "product_id": "理财产品ID，关联wealth_product.id",
            "channel_id": "渠道ID，关联dim_channel.id",
            "order_type": "订单类型：purchase申购/redeem赎回",
            "order_status": "订单状态：submitted已提交/confirmed已确认/cancelled已取消/failed失败",
            "currency_code": "币种代码",
            "order_amount": "订单金额",
            "order_share": "订单份额",
            "confirmed_amount": "确认金额",
            "confirmed_share": "确认份额",
            "fee_amount": "手续费",
            "submitted_at": "提交时间",
            "confirmed_at": "确认时间",
            "cancelled_at": "取消时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "wealth_position": {
        "description": "理财持仓表，维护客户持有理财产品的份额、市值和收益",
        "columns": {
            "id": "持仓ID",
            "customer_id": "客户ID，关联customer.id",
            "account_id": "账户ID，关联bank_account.id",
            "product_id": "理财产品ID，关联wealth_product.id",
            "currency_code": "币种代码",
            "holding_share": "持有份额",
            "available_share": "可用份额",
            "frozen_share": "冻结份额",
            "cost_amount": "成本金额",
            "market_value_amount": "市值金额",
            "accumulated_income_amount": "累计收益金额",
            "last_nav": "最新净值",
            "last_valuation_date": "最新估值日期",
            "position_status": "持仓状态：active持有/closed已结清",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "wealth_income": {
        "description": "理财收益表，记录理财产品的每日收益",
        "columns": {
            "id": "收益ID",
            "customer_id": "客户ID",
            "account_id": "账户ID",
            "position_id": "持仓ID",
            "product_id": "理财产品ID",
            "income_date": "收益日期",
            "income_type": "收益类型：daily_daily日收益/settlement结算收益",
            "currency_code": "币种代码",
            "income_amount": "收益金额",
            "settled_flag": "是否已结算：1是0否",
            "settled_at": "结算时间",
            "created_at": "创建时间",
        },
    },
    "loan_product": {
        "description": "贷款产品表，维护贷款类型、利率和额度范围",
        "columns": {
            "id": "贷款产品ID",
            "product_code": "产品编码",
            "product_name": "产品名称",
            "category_id": "产品分类ID，关联dim_product_category.id",
            "currency_code": "币种代码",
            "loan_type": "贷款类型：consumption消费/operation经营/mortgage按揭/credit信用",
            "min_amount": "最低贷款金额",
            "max_amount": "最高贷款金额",
            "min_term": "最短期限(月)",
            "max_term": "最长期限(月)",
            "annual_rate": "年利率",
            "repayment_method": "还款方式：equal_installment等额本息/equal_principal等额本金/bullet到期还本付息",
            "product_status": "产品状态：draft草稿/active启用/paused暂停/offline下线",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "loan_application": {
        "description": "贷款申请表，记录客户提交的贷款申请",
        "columns": {
            "id": "申请ID",
            "application_no": "申请编号",
            "customer_id": "客户ID，关联customer.id",
            "product_id": "贷款产品ID，关联loan_product.id",
            "branch_id": "申请机构ID，关联dim_branch.id",
            "channel_id": "申请渠道ID，关联dim_channel.id",
            "apply_amount": "申请金额",
            "apply_term": "申请期限(月)",
            "application_status": "申请状态：submitted已提交/approved已批准/rejected已拒绝/cancelled已取消",
            "submitted_at": "提交时间",
            "approved_at": "审批时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "loan_contract": {
        "description": "贷款合同表，记录审批通过后生成的贷款合同",
        "columns": {
            "id": "合同ID",
            "contract_no": "合同编号",
            "customer_id": "客户ID，关联customer.id",
            "application_id": "贷款申请ID，关联loan_application.id",
            "product_id": "贷款产品ID，关联loan_product.id",
            "branch_id": "签约机构ID，关联dim_branch.id",
            "contract_amount": "合同金额",
            "contract_term": "合同期限(月)",
            "annual_rate": "合同年利率",
            "repayment_method": "还款方式",
            "contract_status": "合同状态：pending_disbursement待放款/discharging放款中/active正常/repaid已结清/overdue逾期/written_off核销",
            "signed_at": "签约时间",
            "disbursed_at": "放款时间",
            "matured_at": "到期时间",
            "closed_at": "结清时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "loan_disbursement": {
        "description": "放款记录表，记录贷款合同的实际放款",
        "columns": {
            "id": "放款ID",
            "disbursement_no": "放款编号",
            "contract_id": "合同ID，关联loan_contract.id",
            "customer_id": "客户ID，关联customer.id",
            "disbursement_amount": "放款金额",
            "currency_code": "币种代码",
            "disbursement_status": "放款状态：success成功/failed失败",
            "disbursed_at": "放款时间",
            "created_at": "创建时间",
        },
    },
    "credit_limit": {
        "description": "授信额度表，记录客户授信额度和可用额度",
        "columns": {
            "id": "授信ID",
            "customer_id": "客户ID，关联customer.id",
            "credit_no": "授信编号",
            "credit_amount": "授信额度",
            "used_amount": "已用额度",
            "available_amount": "可用额度",
            "credit_status": "授信状态：active有效/expired过期/frozen冻结/closed关闭",
            "effective_at": "生效时间",
            "expire_at": "过期时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "repayment_schedule": {
        "description": "还款计划表，记录每期应还本金、利息和还款日",
        "columns": {
            "id": "还款计划ID",
            "contract_id": "合同ID，关联loan_contract.id",
            "customer_id": "客户ID，关联customer.id",
            "period_no": "期次",
            "due_date": "应还日期",
            "due_principal": "应还本金",
            "due_interest": "应还利息",
            "due_amount": "应还总额",
            "remaining_principal": "剩余本金",
            "schedule_status": "计划状态：pending待还款/paid已还/overdue逾期",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "repayment_record": {
        "description": "还款记录表，记录客户实际还款",
        "columns": {
            "id": "还款记录ID",
            "repayment_no": "还款编号",
            "contract_id": "合同ID，关联loan_contract.id",
            "customer_id": "客户ID，关联customer.id",
            "repayment_amount": "还款金额",
            "principal_amount": "还本金额",
            "interest_amount": "还息金额",
            "repayment_type": "还款类型：normal正常/early提前/overdue逾期",
            "repayment_status": "还款状态：success成功/failed失败",
            "repaid_at": "还款时间",
            "created_at": "创建时间",
        },
    },
    "overdue_record": {
        "description": "逾期记录表，记录贷款逾期信息",
        "columns": {
            "id": "逾期ID",
            "contract_id": "合同ID，关联loan_contract.id",
            "customer_id": "客户ID，关联customer.id",
            "overdue_principal": "逾期本金",
            "overdue_interest": "逾期利息",
            "overdue_amount": "逾期总额",
            "overdue_days": "逾期天数",
            "overdue_stage": "逾期阶段：m1_1到30天/m2_31到60天/m3_61到90天/m4_91到180天/m5_180天以上",
            "overdue_status": "逾期状态：active逾期中/repaid已还/closed已关闭",
            "occurred_at": "逾期发生时间",
            "resolved_at": "逾期解决时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "fee_reduction": {
        "description": "费用减免表，记录逾期费用减免",
        "columns": {
            "id": "减免ID",
            "reduction_no": "减免编号",
            "contract_id": "合同ID，关联loan_contract.id",
            "customer_id": "客户ID，关联customer.id",
            "reduction_type": "减免类型：penalty_penalty罚息/late_fee滞纳金/compound_interest复利",
            "reduction_amount": "减免金额",
            "reduction_reason": "减免原因",
            "approved_by": "审批人ID，关联dim_employee.id",
            "reduction_status": "减免状态：pending待审批/approved已批准/rejected已拒绝",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "risk_rule": {
        "description": "风控规则表，维护风控规则配置",
        "columns": {
            "id": "规则ID",
            "rule_code": "规则编码",
            "rule_name": "规则名称",
            "rule_type": "规则类型：fraud反欺诈/aml反洗钱/credit信用风险/compliance合规",
            "rule_category": "规则分类",
            "risk_level_id": "风险等级ID，关联dim_risk_level.id",
            "rule_status": "规则状态：active启用/disabled停用",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "risk_strategy": {
        "description": "风控策略表，维护风控策略配置",
        "columns": {
            "id": "策略ID",
            "strategy_code": "策略编码",
            "strategy_name": "策略名称",
            "strategy_type": "策略类型",
            "strategy_status": "策略状态：active启用/disabled停用",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "risk_event": {
        "description": "风险事件表，记录风控规则命中产生的事件",
        "columns": {
            "id": "事件ID",
            "event_no": "事件编号",
            "rule_id": "规则ID，关联risk_rule.id",
            "strategy_id": "策略ID，关联risk_strategy.id",
            "customer_id": "客户ID，关联customer.id",
            "event_type": "事件类型：fraud反欺诈/aml反洗钱/credit信用风险",
            "risk_level_id": "事件风险等级ID，关联dim_risk_level.id",
            "event_status": "事件状态：pending待处理/processing处理中/resolved已处理/closed已关闭",
            "occurred_at": "发生时间",
            "resolved_at": "处理时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "risk_hit_record": {
        "description": "规则命中记录表，记录风控规则命中的详细信息",
        "columns": {
            "id": "命中记录ID",
            "event_id": "风险事件ID，关联risk_event.id",
            "rule_id": "规则ID，关联risk_rule.id",
            "customer_id": "客户ID，关联customer.id",
            "hit_result": "命中结果：hit命中/miss未命中",
            "hit_detail": "命中详情",
            "hit_at": "命中时间",
            "created_at": "创建时间",
        },
    },
    "blacklist_record": {
        "description": "黑名单记录表，维护客户黑名单信息",
        "columns": {
            "id": "黑名单ID",
            "customer_id": "客户ID，关联customer.id",
            "blacklist_type": "黑名单类型：fraud欺诈/aml反洗钱/credit信用风险/high_risk高风险",
            "risk_level_id": "风险等级ID，关联dim_risk_level.id",
            "blacklist_reason": "加入原因",
            "blacklist_status": "状态：active生效/removed已移除",
            "added_at": "加入时间",
            "removed_at": "移除时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "aml_case": {
        "description": "反洗钱案件表，记录反洗钱可疑交易案件",
        "columns": {
            "id": "案件ID",
            "case_no": "案件编号",
            "customer_id": "客户ID，关联customer.id",
            "case_type": "案件类型：suspicious可疑/confirmed确认/false_positive误报",
            "case_status": "案件状态：pending待处理/investigating调查中/reported已上报/closed已关闭",
            "reported_at": "上报时间",
            "closed_at": "关闭时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "manual_review_task": {
        "description": "人工复核任务表，记录需要人工审核的任务",
        "columns": {
            "id": "复核任务ID",
            "task_no": "任务编号",
            "related_type": "关联对象类型：loan_application/credit_application/risk_event/aml_case",
            "related_id": "关联对象ID",
            "assignee_id": "审核人ID，关联dim_employee.id",
            "review_type": "复核类型：loan_approval贷款审批/risk_review风控复核/aml_review反洗钱复核",
            "review_result": "复核结果：approved通过/rejected拒绝/returned退回",
            "task_status": "任务状态：pending待审核/in_progress审核中/completed已完成",
            "assigned_at": "分配时间",
            "completed_at": "完成时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "collection_case": {
        "description": "催收案件表，记录逾期催收案件",
        "columns": {
            "id": "催收案件ID",
            "case_no": "案件编号",
            "contract_id": "合同ID，关联loan_contract.id",
            "customer_id": "客户ID，关联customer.id",
            "assignee_id": "催收员ID，关联dim_employee.id",
            "overdue_amount": "逾期金额",
            "collection_type": "催收类型：sms短信/phone电话/visit上门/legal法律",
            "case_status": "案件状态：pending待处理/in_progress催收中/promise_paid承诺还款/resolved已解决/closed已关闭",
            "assigned_at": "分配时间",
            "resolved_at": "解决时间",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "collection_contact_record": {
        "description": "催收联系记录表，记录催收员的联系过程",
        "columns": {
            "id": "联系记录ID",
            "case_id": "催收案件ID，关联collection_case.id",
            "contact_type": "联系类型：sms短信/phone电话/visit上门",
            "contact_result": "联系结果：reached已联系/unreachable无法联系/promise_paid承诺还款/refused拒绝",
            "contact_content": "联系内容",
            "contacted_at": "联系时间",
            "created_at": "创建时间",
        },
    },
    "collection_performance_daily": {
        "description": "催收绩效日表，记录催收员每日催收绩效",
        "columns": {
            "id": "绩效ID",
            "assignee_id": "催收员ID，关联dim_employee.id",
            "stat_date": "统计日期",
            "total_cases": "总案件数",
            "resolved_cases": "已解决案件数",
            "recovered_amount": "回收金额",
            "recovery_rate": "回收率",
            "created_at": "创建时间",
        },
    },
    "account_product": {
        "description": "账户产品表，维护账户类型、开户条件、限额和费率",
        "columns": {
            "id": "产品ID",
            "product_code": "产品编码",
            "product_name": "产品名称",
            "category_id": "产品分类ID，关联dim_product_category.id",
            "currency_code": "币种代码",
            "account_type": "账户类型：demand_deposit活期/settlement结算/loan_repayment贷款还款/wealth_settlement理财结算",
            "min_open_amount": "最低开户金额",
            "daily_transfer_limit": "日转账限额",
            "daily_withdraw_limit": "日提现限额",
            "annual_fee_amount": "年费金额",
            "product_status": "产品状态：draft草稿/active启用/paused暂停/offline下线",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "service_product": {
        "description": "服务产品表，维护服务包、服务费用和适用渠道",
        "columns": {
            "id": "服务产品ID",
            "service_code": "服务编码",
            "service_name": "服务名称",
            "category_id": "产品分类ID，关联dim_product_category.id",
            "currency_code": "币种代码",
            "service_type": "服务类型：account_service/transaction_service/wealth_service/loan_service/support_service",
            "fee_amount": "服务费用金额",
            "service_status": "服务状态：draft草稿/active启用/paused暂停/offline下线",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
    "business_stat_daily": {
        "description": "业务统计日表，记录各维度的业务统计数据",
        "columns": {
            "id": "统计ID",
            "stat_date": "统计日期",
            "metric_code": "指标编码，关联business_metric_dict.metric_code",
            "dimension_type": "维度类型：branch机构/channel渠道/customer_type客户类型/product_type产品类型",
            "dimension_value": "维度值",
            "metric_value": "指标值",
            "created_at": "创建时间",
        },
    },
    "business_metric_dict": {
        "description": "业务指标字典表，维护指标编码、名称和口径",
        "columns": {
            "id": "指标ID",
            "metric_code": "指标编码",
            "metric_name": "指标名称",
            "metric_category": "指标分类：customer客户/account账户/transaction交易/wealth理财/loan贷款/repayment还款/risk风控/collection催收",
            "calc_expression": "计算口径",
            "unit": "单位",
            "yn": "是否启用",
            "created_at": "创建时间",
            "updated_at": "更新时间",
        },
    },
}

TABLE_RELATIONSHIPS = """
-- 基础维度关系
dim_branch.id -> dim_employee.branch_id (员工归属机构)
dim_branch.id -> customer.branch_id (客户归属机构)
dim_branch.id -> bank_account.branch_id (账户开户机构)
dim_branch.id -> loan_application.branch_id (贷款申请机构)
dim_branch.id -> loan_contract.branch_id (贷款签约机构)

-- 渠道关系
dim_channel.id -> customer.register_channel_id (客户注册渠道)
dim_channel.id -> account_transaction.channel_id (交易渠道)
dim_channel.id -> channel_transaction.channel_id (渠道交易)
dim_channel.id -> loan_application.channel_id (贷款申请渠道)
dim_channel.id -> wealth_order.channel_id (理财订单渠道)

-- 风险等级关系
dim_risk_level.id -> customer.risk_level_id (客户风险等级)
dim_risk_level.id -> customer_risk_assessment.risk_level_id (测评风险等级)
dim_risk_level.id -> wealth_product.risk_level_id (产品风险等级)
dim_risk_level.id -> risk_event.risk_level_id (事件风险等级)
dim_risk_level.id -> blacklist_record.risk_level_id (黑名单风险等级)

-- 客户域关系
customer.id -> customer_identity.customer_id (客户实名)
customer.id -> customer_kyc.customer_id (客户KYC)
customer.id -> customer_risk_assessment.customer_id (客户风险测评)
customer.id -> customer_tag_rel.customer_id (客户标签关系)
customer_tag.id -> customer_tag_rel.tag_id (标签关系)
customer.id -> bank_account.customer_id (客户账户)
customer.id -> account_transaction.customer_id (客户交易)
customer.id -> wealth_order.customer_id (客户理财订单)
customer.id -> wealth_position.customer_id (客户理财持仓)
customer.id -> loan_application.customer_id (客户贷款申请)
customer.id -> loan_contract.customer_id (客户贷款合同)
customer.id -> repayment_schedule.customer_id (客户还款计划)
customer.id -> repayment_record.customer_id (客户还款记录)
customer.id -> overdue_record.customer_id (客户逾期记录)
customer.id -> risk_event.customer_id (客户风险事件)
customer.id -> blacklist_record.customer_id (客户黑名单)
customer.id -> collection_case.customer_id (客户催收案件)
customer.id -> credit_limit.customer_id (客户授信额度)

-- 账户域关系
bank_account.id -> account_transaction.account_id (账户交易)
bank_account.id -> wealth_order.account_id (理财订单账户)
bank_account.id -> wealth_position.account_id (理财持仓账户)

-- 理财域关系
wealth_product.id -> wealth_order.product_id (理财订单产品)
wealth_product.id -> wealth_position.product_id (理财持仓产品)
wealth_product.id -> wealth_income.product_id (理财收益产品)
wealth_product.id -> wealth_nav.product_id (产品净值)
wealth_product.id -> wealth_product_notice.product_id (产品公告)

-- 信贷域关系
loan_product.id -> loan_application.product_id (贷款申请产品)
loan_application.id -> loan_contract.application_id (贷款合同申请)
loan_contract.id -> loan_disbursement.contract_id (放款合同)
loan_contract.id -> repayment_schedule.contract_id (还款计划合同)
loan_contract.id -> repayment_record.contract_id (还款记录合同)
loan_contract.id -> overdue_record.contract_id (逾期记录合同)
loan_contract.id -> collection_case.contract_id (催收案件合同)
loan_contract.id -> fee_reduction.contract_id (费用减免合同)

-- 风控域关系
risk_rule.id -> risk_event.rule_id (事件规则)
risk_rule.id -> risk_hit_record.rule_id (命中规则)
risk_strategy.id -> risk_event.strategy_id (事件策略)
risk_event.id -> risk_hit_record.event_id (命中事件)
dim_employee.id -> manual_review_task.assignee_id (复核审核人)

-- 催收域关系
collection_case.id -> collection_contact_record.case_id (催收联系记录)
dim_employee.id -> collection_case.assignee_id (催收员)
dim_employee.id -> collection_performance_daily.assignee_id (催收绩效)

-- 产品分类关系
dim_product_category.id -> account_product.category_id (账户产品分类)
dim_product_category.id -> loan_product.category_id (贷款产品分类)
dim_product_category.id -> wealth_product.category_id (理财产品分类)
dim_product_category.id -> service_product.category_id (服务产品分类)
"""

SYNONYM_MAP: dict[str, list[str]] = {
    "客户数": ["用户数", "客户数量", "用户数量"],
    "新增客户": ["新客户", "新注册客户", "新开户客户"],
    "活跃客户": ["活跃用户", "有效客户"],
    "放款额": ["放款金额", "放款总额", "贷款发放额"],
    "贷款余额": ["贷款余额", "贷款本金余额", "借据余额"],
    "理财规模": ["AUM", "理财持仓规模", "理财管理规模"],
    "逾期余额": ["逾期金额", "逾期总额", "逾期本金"],
    "交易金额": ["交易总额", "成交金额", "交易额"],
    "交易笔数": ["交易次数", "交易量"],
    "还款金额": ["还款总额", "还款额"],
    "催收回收率": ["催收回收比例", "回收率"],
    "风险事件": ["风控事件", "风险预警"],
}


def build_schema_prompt() -> str:
    lines = ["## 数据库表结构\n"]
    for table_name, meta in TABLE_METADATA.items():
        lines.append(f"### {table_name}")
        lines.append(f"说明：{meta['description']}")
        lines.append("字段：")
        for col, desc in meta["columns"].items():
            lines.append(f"  - {col}: {desc}")
        lines.append("")
    lines.append("## 表关系")
    lines.append(TABLE_RELATIONSHIPS)
    return "\n".join(lines)