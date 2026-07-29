import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from ..config import RuntimeConfig


class LLMAdapter:
    """A thin, configurable adapter for local and remote risk summarization in CI and review flows."""

    def __init__(self, provider: str = "deepseek", api_key: Optional[str] = None, base_url: Optional[str] = None, config_path: Optional[Path] = None, use_remote: bool = True) -> None:
        self.provider = provider
        self.config_path = config_path
        self.use_remote = use_remote
        self.runtime_config = RuntimeConfig.from_file(config_path)
        self.mode = self.runtime_config.mode
        self.enable_llm = self.runtime_config.enable_llm or self.mode == "llm"
        self.api_key = api_key or self.runtime_config.api_key or self._read_config_value("api_key") or os.getenv("SPECOMEGA_API_KEY")
        self.base_url = base_url or self.runtime_config.base_url or self._read_config_value("base_url") or os.getenv("SPECOMEGA_BASE_URL") or "https://api.deepseek.com"
        self.model = self.runtime_config.model or self._read_config_value("model") or os.getenv("SPECOMEGA_MODEL", "deepseek-chat")
        self.llm_threshold = self.runtime_config.llm_threshold
        self.last_status = "initialized"
        self.last_error = None
        self.log_path = Path(".specomega/runtime_mode.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_config_value(self, key: str) -> Optional[str]:
        if not self.config_path or not self.config_path.exists():
            return None
        try:
            payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        except Exception:
            return None
        return payload.get(key)

    def summarize_risk(self, spec: str, trace: Optional[Dict] = None, findings: Optional[List[Dict]] = None) -> Dict:
        """Produce a structured risk summary that can fall back to local rules when LLM access is unavailable."""
        trace = trace or {}
        findings = findings or []
        risk_level = trace.get("risk_level") or ("warning" if findings else "ok")

        if not self.use_remote:
            self.last_status = "remote_disabled"
            self._append_log(f"remote_disabled mode={self.mode} enable_llm={self.enable_llm} threshold={self.llm_threshold} risk_level={risk_level}")
        elif self.enable_llm and self.api_key and self.runtime_config.should_use_llm(risk_level):
            try:
                import urllib.request
                payload = json.dumps({
                    "model": os.getenv("SPECOMEGA_MODEL", "deepseek-chat"),
                    "messages": [
                        {"role": "system", "content": "You are a risk analysis assistant for Agent systems."},
                        {"role": "user", "content": f"Analyze this Agent risk scenario. Spec: {spec}. Trace: {json.dumps(trace)}. Findings: {json.dumps(findings)}"},
                    ],
                }).encode("utf-8")
                req = urllib.request.Request(
                    self.base_url.rstrip("/") + "/chat/completions",
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content:
                        self.last_status = "llm_remote"
                        self._append_log(f"llm_remote mode={self.mode} model={self.model} threshold={self.llm_threshold} risk_level={risk_level}")
                        return {
                            "provider": self.provider,
                            "summary": content,
                            "entities": self._extract_entities(spec, trace),
                            "relationships": self._extract_relationships(trace),
                            "remote": True,
                            "mode": self.mode,
                            "status": self.last_status,
                        }
            except Exception as exc:
                self.last_error = str(exc)
                self.last_status = "llm_fallback"
                self._append_log(f"llm_fallback mode={self.mode} error={exc}")

        if self.mode == "engine" or not self.enable_llm:
            summary = "风险分析：当前运行在工程模式（内网服务器模式），已关闭大模型增强，优先检查工具调用顺序、状态流转与权限边界。"
        elif not self.runtime_config.should_use_llm(risk_level):
            summary = f"风险分析：当前风险等级为 {risk_level}，未达到配置阈值 {self.llm_threshold}，继续使用工程规则与本地检查。"
        else:
            summary = "风险分析：请优先检查工具调用顺序、状态流转与权限边界。"
        if "risk_check" in spec.lower() and findings:
            if self.mode == "engine" or not self.enable_llm:
                summary += " 规范要求在支付前执行 risk_check，当前轨迹存在前置检查缺失或风险状态异常。"
            elif not self.runtime_config.should_use_llm(risk_level):
                summary += " 规范要求在支付前执行 risk_check，当前轨迹存在前置检查缺失或风险状态异常。"
            else:
                summary = "风险分析：规范要求在支付前执行 risk_check，当前轨迹存在前置检查缺失或风险状态异常。"

        if self.last_status not in {"llm_remote", "llm_fallback", "engine_fallback", "local_fallback", "remote_disabled"}:
            self.last_status = "engine_fallback" if self.mode == "engine" or not self.enable_llm else "local_fallback"
        self._append_log(f"{self.last_status} mode={self.mode} enable_llm={self.enable_llm} threshold={self.llm_threshold} risk_level={risk_level}")
        return {
            "provider": self.provider,
            "summary": summary,
            "entities": self._extract_entities(spec, trace),
            "relationships": self._extract_relationships(trace),
            "remote": False,
            "mode": self.mode,
            "status": self.last_status,
            "error": self.last_error,
        }

    def _append_log(self, message: str) -> None:
        """Persist a best-effort execution trace for debugging and audit review."""
        try:
            self.log_path.write_text(self.log_path.read_text(encoding="utf-8") + f"{message}\n" if self.log_path.exists() else f"{message}\n", encoding="utf-8")
        except Exception:
            # Logging should never interrupt the main analysis flow.
            return

    def _extract_entities(self, spec: str, trace: Dict) -> List[Dict]:
        entities = []
        if "risk_check" in spec.lower():
            entities.append({"name": "risk_check", "type": "tool"})
        if "pay" in spec.lower() or trace.get("tool_calls"):
            entities.append({"name": "pay", "type": "tool"})
        state_name = trace.get("state") or "unknown"
        entities.append({"name": state_name, "type": "state"})
        return entities

    def _extract_relationships(self, trace: Dict) -> List[Dict]:
        relationships = []
        if trace.get("tool_calls"):
            relationships.append({"from": "risk_check", "to": "pay", "type": "depends_on"})
        state = trace.get("state") or "unknown"
        relationships.append({"from": state, "to": "pay", "type": "influences"})
        return relationships
