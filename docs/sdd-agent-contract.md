# SDD 与多 Agent 协作契约

## 目标

为多 Agent 协同场景提供一个足够简洁但可执行的规范契约，以保证任务交接清晰、责任明确、流程可验证，并能在 CI、审计与执行预检查中被自动验证。

## 约定

### 1. 角色声明

使用 `@agent:` 声明参与角色，例如：

```text
@agent: planner
@agent: implementer
@agent: reviewer
```

### 2. 交接声明

使用 `@handoff:` 声明角色之间的交接链路：

```text
@handoff: planner->implementer
@handoff: implementer->reviewer
```

### 3. 验证规则

编排器会检查：

- 每个交接目标角色是否都已声明
- 是否存在断裂的交接链路
- 工作流是否具备可执行的顺序结构
- 角色是否被正确归入阶段、依赖与汇聚点结构
- 是否存在可描述的重试策略与回退策略

### 4. 扩展语法

除了基本角色与交接声明外，当前实现还支持：

```text
@phase: planning
@phase: execution
@retry: implementer:3
@fallback: implementer->reviewer
@join: review_gate
```

这些标记会被编排器转成流程元数据，便于后续执行模拟、审查与治理评估。

## 推荐实践

- 每个任务至少包含 `planner`、`implementer`、`reviewer`
- 所有关键交接都应附带可验证证据
- Review Gate 阶段应保留人工或自动审查的证据链
- 对高风险步骤显式声明重试、回退与汇聚点，减少执行异常时的流程漂移
- 把工作流规格作为工程资产管理，便于后续接入 CI 或审批流水线

## 适用场景

- 复杂需求拆解
- 多 Agent 代码生成与审查
- 规范驱动的协同交付
