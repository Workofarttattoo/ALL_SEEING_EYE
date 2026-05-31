"""Scan result collection and reporting."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.colors import Colors


@dataclass
class Finding:
    cve: str
    confidence: str
    notes: str
    category: str = "remote"
    url: str | None = None
    port: int | None = None
    banner: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanReport:
    target: str
    timestamp: str
    open_ports: list[int] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @classmethod
    def create(cls, target: str) -> "ScanReport":
        return cls(
            target=target,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "target": self.target,
            "timestamp": self.timestamp,
            "open_ports": self.open_ports,
            "findings": [asdict(f) for f in self.findings],
        }
        shodan_findings = [f for f in self.findings if f.category == "shodan"]
        if shodan_findings:
            payload["shodan_enriched"] = True
        return payload

    def save(self, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = self.target.replace(":", "_").replace("/", "_")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = output_dir / f"recon_{safe_name}_{stamp}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2))
        return path

    def print_summary(self) -> None:
        print(f"\n{Colors.BOLD}{'=' * 60}{Colors.END}")
        print(f"{Colors.RED}[!] VULNERABILITY ASSESSMENT COMPLETE{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.END}\n")

        if not self.findings:
            print(
                f"{Colors.GREEN}[+] No obvious indicators detected "
                f"(manual verification recommended){Colors.END}"
            )
            return

        print(
            f"{Colors.RED}[!] {len(self.findings)} POTENTIAL INDICATORS IDENTIFIED:"
            f"{Colors.END}\n"
        )
        for idx, finding in enumerate(self.findings, 1):
            print(f"{Colors.YELLOW}{idx}. {finding.cve}{Colors.END}")
            print(f"   Category: {finding.category}")
            print(f"   Confidence: {finding.confidence}")
            print(f"   Details: {finding.notes}")
            if finding.url:
                print(f"   URL: {finding.url}")
            if finding.port:
                print(f"   Port: {finding.port}")
            if finding.banner:
                print(f"   Banner: {finding.banner}")
            print()
