# SpecOmega

SpecOmega 是一个面向“规范 - 执行 - 验证”闭环的轻量级工程中枢。它不替代 Spec Kit、OpenSpec 或 Superpowers 的主流程，而是为它们提供一个统一的验证层：把规范中的可验证约束转成机器可执行的检查结果，并把多 Agent 协作中的交接规则变成可审计、可执行、可扩展的工程契约。

## 项目定位

SpecOmega 的核心价值在于弥合“规范定义”与“代码执行”之间的验证鸿沟：

> 让规范从“可讨论的文档”变成“可验证的工程资产”，并为多 Agent 协同提供可执行的流程契约。

- 让规范从“可讨论的文档”变成“可验证的工程资产”
- 将人工 Review Gate 中可自动化的部分转成机器检查
- 为多 Agent 协作提供角色、交接与证据链规范

## 当前能力

这个仓库已经包含一个可运行的最小实现，提供：

- 统一验证引擎
- 基于 `@specomega:` 标记的规范验证
- 契约验证器：`contract_check`
- 执行轨迹验证器：`trace_check`
- 安全规则验证器：`security_check`
- 配置驱动的验证器加载
- 多 Agent 工作流编排与交接契约检查
- CLI 入口与报告输出

## 适用场景

- 规范与代码一致性验证
- Spec Kit / OpenSpec / Superpowers 的补充验证层
- 多 Agent 任务的角色与交接规范化
- CI/CD、审计与 Review Gate 的自动化前置检查

## 目录结构

- [specomega](specomega)：核心包
- [tests](tests)：回归测试
- [.specify/specs](.specify/specs)：示例 Spec Kit 规范
- [openspec/specs](openspec/specs)：示例 OpenSpec 规范
- [.specomega](.specomega)：验证策略配置与多 Agent 示例
- [docs](docs)：架构、使用手册与协作契约文档

## 文档索引

- [docs/architecture.md](docs/architecture.md)：架构与职责说明
- [docs/user-guide.md](docs/user-guide.md)：使用手册
- [docs/sdd-agent-contract.md](docs/sdd-agent-contract.md)：SDD 与多 Agent 协作契约

## 快速使用

运行测试：

```bash
python -m unittest discover -s tests -v
```

执行规范验证：

```bash
python -m specomega verify --path .
```

分析规范冲突：

```bash
python -m specomega analyze --path .specify/specs/user_management.spec openspec/specs/user_management.md
```

规划多 Agent 工作流：

```bash
python -m specomega plan --path .specomega/agents.md
```

## 设计定位

- Spec Kit / OpenSpec：定义规范与生成内容
- Superpowers：约束执行纪律
- SpecOmega：验证规范约束与实现证据是否一致

## 多 Agent 与 SDD 方向

当前实现已经把 SpecOmega 的能力扩展到一个轻量的 SDD 风格协同层：

- 使用 `@agent:` 声明角色
- 使用 `@handoff:` 声明角色之间的交接契约
- 通过编排器检查交接是否存在缺失角色
- 作为验证与执行流程的统一入口，支撑多 Agent 任务的规范化执行

示例：

```text
@agent: planner
@agent: implementer
@agent: reviewer
@handoff: planner->implementer
@handoff: implementer->reviewer
```
