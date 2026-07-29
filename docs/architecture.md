# SpecOmega 架构说明

## 目标

SpecOmega 不是一个独立的开发工作流，而是一个面向规范、执行与治理一致性验证的中枢层。它负责把规范中的可验证约束转成机器可执行的检查结果，服务于 Spec Kit、OpenSpec、Superpowers、多 Agent 协作以及生成式代码治理场景，并在 CI 与审计流程中提供可追踪的证据输出。

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

4. Vibecode 审计与治理
   - 检测 Vibecode 相关信号、来源类型与证据
   - 计算风险等级与建议动作
   - 基于策略配置决定是否生成阻断性治理结论

5. 结果输出
   - 提供 CLI 输出、报告文件生成、审计摘要与治理门禁文件

## 组件划分

- `specomega/engine.py`
  - 验证引擎，负责调度验证器并组织结果
- `specomega/verifiers/`
  - 验证器实现，包括契约、轨迹、安全、语法边界与 Vibecode 检查
- `specomega/analysis/vibecode.py`
  - Vibecode 分析器，负责关键词识别、来源分类、风险评分与政策评估
- `specomega/analysis/risk_analyzer.py`
  - 风险分析器，聚合规范、执行轨迹与 Vibecode 线索，生成建议
- `specomega/agents/orchestrator.py`
  - 多 Agent 编排器，用于解析工作流角色和交接规则
- `specomega/cli.py`
  - 命令行入口，暴露验证、冲突分析、工作流规划、风险分析与 Vibecode 审计能力

## 输出产物

- JSON 报告：适合程序化消费与后续集成
- Markdown / HTML / CSV：适合审计、人工 Review 与归档
- SARIF：适合接入静态分析或 CI 检查工具
- `vibecode_gate.txt`：适合作为治理门禁或审批摘要文件

## 设计原则

- 职责隔离：规范定义、执行纪律、治理风险与结果输出保持分层
- 无侵入：通过标记和独立命令即可接入，不需改动外部框架源码
- 可扩展：新增验证器、风险规则或治理策略只需兼容现有接口即可
- 可审计：所有验证结果应可落盘并用于回溯、合规审查与审批追踪
