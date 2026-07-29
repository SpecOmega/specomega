# 开发者指南

## 目标

本文档面向希望参与 SpecOmega 开发、扩展验证能力或贡献修复的开发者。它重点说明项目的组织方式、开发入口、验证方式与推荐的修改范式。

## 1. 项目结构概览

- [specomega](../specomega)：核心 Python 包，包含 CLI、引擎、验证器与分析模块。
- [tests](../tests)：回归测试与行为验证用例。
- [examples](../examples)：示例运行脚本与示例输入。
- [docs](../docs)：架构、使用手册与开发说明。
- [.specomega](../.specomega)：默认配置、示例工作流与报告输出目录。

## 2. 关键模块

- `specomega/cli.py`：命令行入口，负责 `verify`、`analyze`、`plan`、`risk`、`vibecode` 与 `info` 等子命令。
- `specomega/engine.py`：统一验证引擎，负责调度验证器并收敛结果。
- `specomega/verifiers/`：实现合同、轨迹、安全与语法边界检查。
- `specomega/analysis/`：Vibecode 分析、风险分析和框架协同说明模块。
- `specomega/agents/orchestrator.py`：多 Agent 工作流编排逻辑。

## 3. 开发前建议流程

建议先从以下命令开始：

```bash
python -m specomega --version
python -m specomega info
python -m unittest discover -s tests -v
```

这一步能确认 CLI、测试环境和项目入口都已经正常工作。

## 4. 推荐的开发循环

1. 先理解需要修改的子系统：例如验证器、CLI、风险分析或文档。
2. 先补一个回归测试，再实现功能或修复。
3. 运行核心验证命令：

```bash
python -m unittest discover -s tests -v
python examples/agent_runtime/run_example.py
python -m specomega verify --path .
```

4. 如果你修改了工作流、治理规则或报告格式，请同时更新相关文档与示例。

## 5. 修改时的注意事项

- 优先保持 CLI 输出稳定，避免破坏现有脚本或 CI 依赖。
- 对新增命令或改动的报告结构，优先在测试中覆盖。
- 对于治理与审计相关行为，尽量同时维护示例、文档和配置文件。
- 新功能最好能同时兼顾本地规则和 CI 友好性。

## 6. 文档与示例要求

当以下任一项发生变化时，应同步更新：

- CLI 子命令与参数
- 生成的报告格式或文件名
- 验证规则或治理门禁逻辑
- 示例工作流与样例输入

推荐同步更新的文件包括：

- [README.md](../README.md)
- [docs/quickstart.md](./quickstart.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [CHANGELOG.md](../CHANGELOG.md)

## 7. 贡献建议

提交 PR 前，请确认：

- 本地测试已通过
- 相关文档已更新
- 关键行为有回归测试覆盖
- 变更说明清晰、可追踪
