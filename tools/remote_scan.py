#!/usr/bin/env python3
"""Remote-only CVE scanner with extended coverage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.colors import Colors
from lib.remote_checks import port_scan_quick, run_remote_checks
from lib.reporter import ScanReport
from lib.target import Target


def main() -> int:
    parser = argparse.ArgumentParser(description="Remote CVE fingerprint scanner")
    parser.add_argument("target", help="URL, hostname, or IP")
    parser.add_argument("--core-only", action="store_true", help="Skip extended remote checks")
    parser.add_argument("--output-dir", default="reports", help="Report output directory")
    args = parser.parse_args()

    target = Target.from_input(args.target)
    print(
        f"""{Colors.RED}
    ╔═══════════════════════════════════════════════════════════╗
    ║         🔴 REMOTE CVE FINGERPRINT SCANNER 🔴             ║
    ╚═══════════════════════════════════════════════════════════╝{Colors.END}
    Target: {Colors.BOLD}{target.domain}{Colors.END}
    """
    )

    report = ScanReport.create(target.domain)
    try:
        print(f"{Colors.GREEN}[+] Resolved {target.domain} → {target.resolve()}{Colors.END}")
    except OSError as exc:
        print(f"{Colors.RED}[-] DNS resolution failed: {exc}{Colors.END}")
        return 1

    port_scan_quick(target, report)
    run_remote_checks(target, report, extended=not args.core_only)
    report.print_summary()
    path = report.save(Path(args.output_dir))
    print(f"{Colors.CYAN}[*] Report saved to: {path}{Colors.END}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
