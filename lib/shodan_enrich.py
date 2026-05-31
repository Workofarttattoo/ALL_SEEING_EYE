"""Enrich ASE scan reports with Shodan host intelligence."""

from __future__ import annotations

from typing import Any

from lib.reporter import Finding, ScanReport
from lib.shodan_client import ShodanClient, host_to_findings, print_host_summary, resolve_to_ip


def enrich_report(
    report: ScanReport,
    target: str,
    *,
    history: bool = False,
) -> dict[str, Any] | None:
    client = ShodanClient.try_create()
    if not client:
        return None

    ip = resolve_to_ip(target)
    host_data = client.host(ip, history=history)
    print_host_summary(host_data)

    shodan_ports = set(host_data.get("ports") or [])
    report.open_ports = sorted(set(report.open_ports) | shodan_ports)

    for item in host_to_findings(host_data, target):
        report.add(
            Finding(
                cve=item["cve"],
                confidence=item["confidence"],
                notes=item["notes"],
                category=item.get("category", "shodan"),
                port=item.get("port"),
                banner=item.get("banner"),
                extra=item.get("extra", {}),
            )
        )

    return host_data
