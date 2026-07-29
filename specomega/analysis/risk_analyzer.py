import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from .llm_adapter import LLMAdapter
from .vibecode import VibecodeAnalyzer


class RiskAnalyzer:
    """Aggregate agent-risk findings into a structured review report with local and LLM-backed summaries."""

    def analyze(self, spec: str, trace: Optional[Dict] = None, use_remote: bool = False, config_path: Optional[Path] = None, llm_threshold: Optional[str] = None) -> Dict:
        trace = trace or {}
        findings: List[Dict] = []
        recommendations: List[str] = []

        tool_calls = trace.get("tool_calls", [])
        if tool_calls and tool_calls[0] != "risk_check" and "risk_check" in spec.lower():
            findings.append({"type": "tool_sequence", "message": "缺少风险检查前置步骤"})
            recommendations.append("在支付/敏感工具调用前强制插入 risk_check 约束")

        if trace.get("risk_level") == "medium":
            findings.append({"type": "state_risk", "message": "中风险状态下未启用人工确认"})
            recommendations.append("中风险场景下强制要求人工确认，避免越权或误操作")

        if trace.get("repo") and trace.get("action") == "write":
            findings.append({"type": "permission_risk", "message": "存在写操作/越权执行风险"})
            recommendations.append("限制写操作范围并绑定仓库级权限边界")

        vibecode = VibecodeAnalyzer().analyze(spec)
        if vibecode["is_vibecode"]:
            findings.append({"type": "vibecode_signal", "message": f"检测到 Vibecode 相关信号（score={vibecode['score']}）"})
            recommendations.append("为 Vibecode 场景增加显式审查与回滚约束")

        risk_level = "ok"
        if findings:
            risk_level = "warning"

        config_path = config_path or Path(".specomega/llm_config.json")
        llm_adapter = LLMAdapter(provider="deepseek", config_path=config_path, use_remote=use_remote)
        if llm_threshold:
            llm_adapter.runtime_config.llm_threshold = llm_threshold
            llm_adapter.llm_threshold = llm_threshold
        llm_output = llm_adapter.summarize_risk(spec=spec, trace=trace, findings=findings)

        return {
            "risk_level": risk_level,
            "findings": findings,
            "recommendations": recommendations,
            "trace_summary": {
                "tool_calls": tool_calls,
                "risk_level": trace.get("risk_level"),
                "state": trace.get("state"),
                "repo": trace.get("repo"),
                "action": trace.get("action"),
            },
            "llm_summary": llm_output,
            "llm_threshold": llm_adapter.llm_threshold,
            "report_markdown": self._build_markdown_report(risk_level, findings, recommendations, llm_output),
        }

    def _build_markdown_report(self, risk_level: str, findings: List[Dict], recommendations: List[str], llm_output: Dict) -> str:
        lines = ["# Agent Risk Report", "", f"- Risk Level: **{risk_level}**", ""]
        if findings:
            lines.append("## Findings")
            for item in findings:
                lines.append(f"- {item['message']}")
            lines.append("")
        if recommendations:
            lines.append("## Recommendations")
            for item in recommendations:
                lines.append(f"- {item}")
            lines.append("")
        lines.append("## LLM Summary")
        lines.append(llm_output.get("summary", ""))
        return "\n".join(lines)


def analyze_agent_risks(spec: str, trace: Optional[Dict] = None, use_remote: bool = False, config_path: Optional[Path] = None, llm_threshold: Optional[str] = None) -> Dict:
    return RiskAnalyzer().analyze(spec, trace, use_remote=use_remote, config_path=config_path, llm_threshold=llm_threshold)
