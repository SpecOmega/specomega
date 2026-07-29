# SDD 与多 Agent 协作契约

## 目标

为多 Agent 协同场景提供一个足够简洁但可执行的规范契约，以保证任务交接清晰、责任明确、流程可验证。

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

## 推荐实践

- 每个任务至少包含 `planner`、`implementer`、`reviewer`
- 所有关键交接都应附带可验证证据
- Review Gate 阶段应保留人工或自动审查的证据链

## 适用场景

- 复杂需求拆解
- 多 Agent 代码生成与审查
- 规范驱动的协同交付
