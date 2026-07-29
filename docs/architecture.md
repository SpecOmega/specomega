# SpecOmega 架构说明

## 目标

SpecOmega 不是一个独立的开发工作流，而是一个面向规范与实现一致性验证的中枢层。它负责把规范中的可验证约束转成机器可执行的检查结果，服务于 Spec Kit、OpenSpec、Superpowers 与多 Agent 协作场景。

## 核心职责

1. 规范约束提取
   - 解析 `@specomega:` 标记
   - 提取可执行验证要求，如 `contract_check`、`trace_check`、`security_check`

2. 验证执行
   - 调用对应验证器执行检查
   - 产出结构化验证报告

3. 交接与协同规范
   - 通过 `@agent:` 和 `@handoff:` 建立角色关系与流程契约
   - 保障多 Agent 工作流的正确性与可追踪性

4. 结果输出
   - 提供 CLI 输出、报告文件生成和冲突分析能力

## 组件划分

- `specomega/engine.py`
  - 验证引擎，负责调度验证器并组织结果
- `specomega/verifiers/`
  - 验证器实现，包括契约、轨迹、安全与语法边界检查
- `specomega/agents/orchestrator.py`
  - 多 Agent 编排器，用于解析工作流角色和交接规则
- `specomega/cli.py`
  - 命令行入口，暴露验证、冲突分析与工作流规划能力

## 设计原则

- 职责隔离：规范定义、执行纪律与验证结果保持分层
- 无侵入：通过标记和独立命令即可接入，不需改动外部框架源码
- 可扩展：新增验证器或 Agent 角色只需遵循接口和规范即可
- 可审计：所有验证结果应可落盘并用于回溯
