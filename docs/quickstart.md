# Quickstart

## 1. 环境要求

- Python 3.11+
- 终端环境可执行 `python`
- 仓库根目录为当前工作目录

## 2. 安装与初始化

在仓库根目录执行：

```bash
cd /workspaces/specomega
python -m unittest discover -s tests -v
```

这一步会确认当前实现已经可正常运行。

## 3. 运行第一个示例

### 3.1 Agent 工具调用合规性验证

当前仓库内置了一个最小可运行的 Agent 示例：

```bash
python examples/agent_runtime/run_example.py
```

该示例会读取以下文件：

- [examples/agent_runtime/spec.md](../examples/agent_runtime/spec.md)
- [examples/agent_runtime/agent_trace.json](../examples/agent_runtime/agent_trace.json)

它用于验证一个支付场景中的工具调用顺序是否符合规范：

- 先执行 `risk_check`
- 再执行 `pay`

若顺序符合，验证结果会显示为 `passed: true`。

## 4. 运行规范验证

### 4.1 验证整个项目里的规范标记

```bash
python -m specomega verify --path .
```

该命令会扫描当前工程中的 `@specomega:` 标记，并调用相应验证器进行检查。

### 4.2 验证单个规范文件

```bash
python -m specomega verify --path .specify/specs/user_management.spec
```

## 5. 分析规范冲突

当多个规范文件对同一约束给出不同要求时，可执行：

```bash
python -m specomega analyze --path .specify/specs/user_management.spec openspec/specs/user_management.md
```

## 6. 规划多 Agent 工作流

```bash
python -m specomega plan --path .specomega/agents.md
```

该命令会生成一个包含角色与交接约束的工作流计划，帮助你验证多 Agent 协作是否具备基本合法结构。

## 7. 结果文件

验证结果会写入：

- [.specomega/reports/latest.json](../.specomega/reports/latest.json)

这使得验证结果可用于 CI、审计、人工 Review 或后续集成。
