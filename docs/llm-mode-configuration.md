# 大模型模式与工程模式配置

SpecOmega 支持两种运行模式：

- 工程模式（默认）：适合内网服务器、离线或受限环境，优先使用本地规则和工程化分析。
- 大模型模式：当配置启用且具备凭据时，使用远端 LLM 做风险摘要与推理增强。

## 配置入口

运行时模式由 [.specomega/llm_config.json](../.specomega/llm_config.json) 控制。

默认配置如下：

```json
{
  "mode": "engine",
  "enable_llm": false,
  "llm_threshold": "warning"
}
```

若要启用大模型模式，可使用：

```json
{
  "mode": "llm",
  "enable_llm": true,
  "api_key": "your-api-key",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat",
  "llm_threshold": "warning"
}
```

## 阈值策略

新增的 `llm_threshold` 字段用于按风险等级决定是否触发远端 LLM：

- `ok`: 仅在风险等级为 `ok` 时触发
- `warning`: 仅在 `warning` 或更高风险时触发
- `critical`: 仅在 `critical` 风险时触发

当风险等级低于阈值时，系统会自动回退到工程模式规则，避免无意义的远端调用。

## 环境变量

也可以通过环境变量切换：

- `SPECOMEGA_ENABLE_LLM=true`
- `SPECOMEGA_MODE=llm`
- `SPECOMEGA_API_KEY=...`
- `SPECOMEGA_BASE_URL=...`
- `SPECOMEGA_MODEL=...`

当大模型模式关闭时，系统会自动走工程模式（内网服务器模式），避免远端调用。
