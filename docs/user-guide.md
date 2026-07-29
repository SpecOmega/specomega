# SpecOmega 使用手册

## 1. 安装与运行

在仓库根目录执行：

```bash
python -m unittest discover -s tests -v
python -m specomega verify --path .
```

## 2. 验证规范文件

SpecOmega 会扫描包含 `@specomega:` 的规范片段，并执行对应验证器。

示例：

```text
**验证要求**：@specomega: contract_check(page_zero=400)
```

执行：

```bash
python -m specomega verify --path .specify/specs/user_management.spec
```

## 3. 分析规范冲突

当多个规范文件对同一约束给出不同结果时，可执行：

```bash
python -m specomega analyze --path .specify/specs/user_management.spec openspec/specs/user_management.md
```

## 4. 规划多 Agent 工作流

可以通过下面的方式定义多 Agent 协作规范：

```text
@agent: planner
@agent: implementer
@agent: reviewer
@handoff: planner->implementer
@handoff: implementer->reviewer
```

执行：

```bash
python -m specomega plan --path .specomega/agents.md
```

## 5. 风险分析与报告输出

除了规范验证，SpecOmega 还支持面向 Agent 场景的风险分析与报告生成：

```bash
python -m specomega risk --spec examples/agent_runtime/spec.md --trace examples/agent_runtime/agent_trace.json --output-dir .specomega/reports
```

执行后会生成：

- `.specomega/reports/risk_report.json`
- `.specomega/reports/risk_report.md`
- `.specomega/reports/risk_report.sarif`（当使用 `--format sarif`）
- `.specomega/reports/risk_report.html`（当使用 `--format html`）

若配合 `--strict` 使用，且发现风险项时会以状态码 `1` 退出，适合接入 CI。

## 6. 结果输出

验证报告会写入：

- `.specomega/reports/latest.json`

这使得验证结果可被 CI、审计流程或人工 Review 直接消费。
