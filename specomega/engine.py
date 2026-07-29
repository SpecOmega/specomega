import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .verifiers.ast_verifier import AstVerifier
from .verifiers.contract_verifier import ContractVerifier
from .verifiers.security_verifier import SecurityVerifier
from .verifiers.tool_call_verifier import ToolCallVerifier
from .verifiers.trace_verifier import TraceVerifier


class VerificationEngine:
    def __init__(self, verifier_classes=None) -> None:
        self.verifiers = []
        for verifier_cls in verifier_classes or [AstVerifier, ContractVerifier, SecurityVerifier, ToolCallVerifier, TraceVerifier]:
            self.verifiers.append(verifier_cls())

    @classmethod
    def from_config(cls, config_path: Optional[Path] = None) -> "VerificationEngine":
        config_path = config_path or Path(".specomega/config.yaml")
        if not config_path.exists():
            return cls()

        content = config_path.read_text(encoding="utf-8")
        names = [line.strip().split("-", 1)[1].strip() for line in content.splitlines() if line.strip().startswith("- ")]
        registry = {
            "ast_verifier": AstVerifier,
            "contract_verifier": ContractVerifier,
            "security_verifier": SecurityVerifier,
            "tool_call_verifier": ToolCallVerifier,
            "trace_verifier": TraceVerifier,
        }
        verifier_classes = [registry[name] for name in names if name in registry]
        return cls(verifier_classes=verifier_classes or None)

    def verify(self, spec_fragment: str, context: Optional[Dict] = None) -> Dict:
        context = context or {}
        results: List[Dict] = []
        for match in re.finditer(r"@specomega:\s*([^\n]+)", spec_fragment):
            tag = match.group(1).strip()
            for verifier in self.verifiers:
                if verifier.can_handle(tag):
                    passed, failures, evidence = verifier.verify(tag, context)
                    results.append({
                        "tag": tag,
                        "passed": passed,
                        "failures": failures,
                        "evidence": evidence,
                    })
                    break
        return {"results": results}

    def write_report(self, report: Dict, output_path: Optional[Path] = None) -> Path:
        target = output_path or Path(".specomega/reports/latest.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return target
