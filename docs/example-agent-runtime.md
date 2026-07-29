# Agent 示例落地使用说明

## 目标

该示例展示了 SpecOmega 如何在真实 Agent 场景中把“工具调用规范”转化为可自动验证的工程约束。

## 场景说明

在支付类 Agent 场景中，规范要求：

1. 必须先调用 `risk_check`
2. 只有在风险等级为 `safe` 时才能调用 `pay`
3. 如果风险等级为 `medium`，需要人工确认

## 示例文件

- [examples/agent_runtime/spec.md](../examples/agent_runtime/spec.md)：规范定义
- [examples/agent_runtime/agent_trace.json](../examples/agent_runtime/agent_trace.json)：Agent 执行轨迹
- [examples/agent_runtime/run_example.py](../examples/agent_runtime/run_example.py)：执行脚本

## 运行方式

```bash
cd /workspaces/specomega
python examples/agent_runtime/run_example.py
```

## 预期结果

如果规范与执行轨迹一致，输出结果会包含：

```json
{
  "results": [
    {
      "passed": true,
      "failures": []
    }
  ]
}
```

## 落地建议

- 在实际项目中，可以将 `agent_trace.json` 替换为真实的 Agent 日志或运行时事件流。
- 规范中的 `@specomega:` 标记可以扩展为更多验证规则，例如：
  - 工具调用顺序
  - 决策路径合法性
  - 沙箱边界与权限控制
- 该示例可作为 CI 阶段的自动化前置检查。

## 与真实项目集成方式

### 1. 开发阶段

在 Prompt、Tool Schema 或规范文档中声明验证点。

### 2. CI 阶段

在构建或测试流程中执行：

```bash
python -m specomega verify --path .
```

### 3. 运行时

在生产 Agent 启动或关键动作前，加载验证规则并执行实时检查。
