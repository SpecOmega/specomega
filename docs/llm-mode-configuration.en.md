# LLM Mode Configuration

SpecOmega supports two runtime modes:

- Engine mode: default, offline-friendly, suitable for intranet or internal server environments.
- LLM mode: enables remote LLM-based summarization when configuration and credentials are present.

## Configuration

The runtime mode is controlled by [.specomega/llm_config.json](../.specomega/llm_config.json).

Example:

```json
{
  "mode": "engine",
  "enable_llm": false
}
```

To enable LLM mode:

```json
{
  "mode": "llm",
  "enable_llm": true,
  "api_key": "your-api-key",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}
```

## Environment variables

You can also use:

- `SPECOMEGA_ENABLE_LLM=true`
- `SPECOMEGA_MODE=llm`
- `SPECOMEGA_API_KEY=...`
- `SPECOMEGA_BASE_URL=...`
- `SPECOMEGA_MODEL=...`

When LLM mode is disabled, SpecOmega uses the engineering/offline path and avoids remote calls.
