## [BOUNDARY-001] 分页参数校验
GIVEN `page=0`
WHEN 请求用户列表
THEN 必须返回 400 错误
**验证要求**：@specomega: contract_check(page_zero=400)
**关键性**：CRITICAL
