import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RuntimeConfig:
    mode: str = "engine"
    enable_llm: bool = False
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    llm_threshold: str = "warning"
    config_path: Optional[Path] = None
    last_loaded_at: Optional[float] = None

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "RuntimeConfig":
        config_path = Path(config_path) if config_path else Path(".specomega/llm_config.json")
        if not config_path.exists():
            return cls(config_path=config_path)
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            return cls(config_path=config_path)

        mode = payload.get("mode") or ("llm" if payload.get("enable_llm") else "engine")
        threshold = payload.get("llm_threshold") or os.getenv("SPECOMEGA_LLM_THRESHOLD") or "warning"
        return cls(
            mode=str(mode).lower(),
            enable_llm=bool(payload.get("enable_llm", False)),
            api_key=payload.get("api_key") or os.getenv("SPECOMEGA_API_KEY"),
            base_url=payload.get("base_url") or os.getenv("SPECOMEGA_BASE_URL"),
            model=payload.get("model") or os.getenv("SPECOMEGA_MODEL"),
            llm_threshold=str(threshold).strip().lower(),
            config_path=config_path,
            last_loaded_at=os.path.getmtime(config_path) if config_path.exists() else None,
        )

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        mode = os.getenv("SPECOMEGA_MODE", "engine")
        enable_llm = os.getenv("SPECOMEGA_ENABLE_LLM", "false").lower() in {"1", "true", "yes", "on"}
        threshold = os.getenv("SPECOMEGA_LLM_THRESHOLD", "warning")
        return cls(mode=mode, enable_llm=enable_llm, llm_threshold=threshold)

    def refresh(self) -> "RuntimeConfig":
        return self.from_file(self.config_path)

    def should_use_llm(self, risk_level: Optional[str] = None) -> bool:
        if not self.enable_llm or self.mode == "engine":
            return False
        normalized_level = self._normalize_risk_level(risk_level)
        threshold_level = self._normalize_risk_level(self.llm_threshold)
        return self._risk_level_rank(normalized_level) >= self._risk_level_rank(threshold_level)

    @staticmethod
    def _normalize_risk_level(risk_level: Optional[str]) -> str:
        if risk_level is None:
            return "ok"
        value = str(risk_level).strip().lower()
        mapping = {
            "safe": "ok",
            "ok": "ok",
            "info": "info",
            "notice": "info",
            "warning": "warning",
            "warn": "warning",
            "medium": "warning",
            "moderate": "warning",
            "high": "critical",
            "critical": "critical",
            "urgent": "critical",
            "severe": "critical",
        }
        return mapping.get(value, value)

    @staticmethod
    def _risk_level_rank(risk_level: str) -> int:
        return {"ok": 0, "info": 1, "warning": 2, "critical": 3}.get(risk_level, 2)
