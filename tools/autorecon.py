#!/usr/bin/env python3
"""Autonomous red team reconnaissance — detection and fingerprinting only."""

from __future__ import annotations

import argparse
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.colors import Colors
from lib.local_checks import run_local_checks
from lib.remote_checks import port_scan_quick, run_remote_checks
from lib.reporter import ScanReport
from lib.target import Target


def banner(target: str, aggressive: bool) -> None:
    mode = "AGGRESSIVE" if aggressive else "STANDARD"
    print(
        f"""{Colors.RED}
    ╔═══════════════════════════════════════════════════════════╗
    ║           🔴 ALL_SEEING_EYE AUTORECON v1.0 🔴            ║
    ║              Authorized Recon — Detection Only            ║
    ╚═══════════════════════════════════════════════════════════╝{Colors.END}
    Target: {Colors.BOLD}{target}{Colors.END}
    Mode: {Colors.YELLOW}{mode}{Colors.END}
    """
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Autonomous CVE-focused recon scanner")
    parser.add_argument("target", nargs="?", help="URL, hostname, or IP")
    parser.add_argument("--aggressive", action="store_true", help="Include extended remote checks")
    parser.add_argument("--local", action="store_true", help="Run local system checks instead of remote")
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory for JSON reports (default: reports)",
    )
    args = parser.parse_args()

    if args.local:
        host = platform.node() or "localhost"
        banner(host, args.aggressive)
        report = ScanReport.create(host)
        run_local_checks(report)
        report.print_summary()
        path = report.save(Path(args.output_dir))
        print(f"{Colors.CYAN}[*] Report saved to: {path}{Colors.END}")
        return 0

    if not args.target:
        parser.error("target is required unless --local is set")

    target = Target.from_input(args.target)
    banner(target.domain, args.aggressive)
    report = ScanReport.create(target.domain)

    try:
        ip = target.resolve()
        print(f"{Colors.GREEN}[+] Resolved {target.domain} → {ip}{Colors.END}")
    except OSError as exc:
        print(f"{Colors.RED}[-] Failed to resolve target: {exc}{Colors.END}")
        return 1

    port_scan_quick(target, report)
    run_remote_checks(target, report, extended=args.aggressive)
    report.print_summary()
    path = report.save(Path(args.output_dir))
    print(f"{Colors.CYAN}[*] Report saved to: {path}{Colors.END}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
