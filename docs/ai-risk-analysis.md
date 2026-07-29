# AI 风险分析与优化建议

## 目标

SpecOmega 的正式版本可以为 Agent 项目提供一层面向大模型能力的风险分析能力：

- 识别潜在风险点
- 分析本体关联关系、调用关系与状态流转
- 输出结构化风险报告与优化建议

## 当前能力

当前实现提供了一个面向工程治理的分析器，能够从规范与运行轨迹中自动识别：

- 工具调用顺序风险
- 中风险状态下缺少人工确认
- 权限/写操作越权风险

## 运行方式

### 本地模式（默认）

```bash
python -m specomega risk --spec examples/agent_runtime/spec.md --trace examples/agent_runtime/agent_trace.json
```

### 接入 DeepSeek / OpenAI 兼容接口

设置环境变量后，适配器会尝试使用远程模型进行摘要生成：

```bash
export SPECOMEGA_API_KEY=your_api_key
export SPECOMEGA_BASE_URL=https://api.deepseek.com
export SPECOMEGA_MODEL=deepseek-chat
python -m specomega risk --spec examples/agent_runtime/spec.md --trace examples/agent_runtime/agent_trace.json
```

## 输出示例

```json
{
  "risk_level": "warning",
  "findings": [
    {
      "type": "tool_sequence",
      "message": "缺少风险检查前置步骤"
    }
  ],
  "recommendations": [
    "在支付/敏感工具调用前强制插入 risk_check 约束"
  ]
}
```

## 适用场景

- 支付/风控/权限敏感类 Agent
- 多 Agent 协作中的状态与调用链审计
- 结合大模型能力对规范与执行轨迹进行风险排查

## 后续扩展方向

- 对接 DeepSeek / OpenAI / Anthropic 等模型接口
- 引入更细粒度的依赖图和调用图分析
- 将风险分析结果与 CI、Review Gate、审计日志联动
