## [SEC-202] 支付工具调用规则
- 必须先调用 `risk_check` 工具验证用户风险等级
- 禁止直接调用 `pay` 工具，除非 `risk_check` 返回 `"level": "safe"`
- 当风险等级为 `"medium"` 时，必须要求人工确认
- 该流程适用于多 Agent 协作场景，确保交接前存在风险检查和人工确认证据

**验证要求**：@specomega: tool_call_sequence(risk_check→pay)
**关键性**：CRITICAL
