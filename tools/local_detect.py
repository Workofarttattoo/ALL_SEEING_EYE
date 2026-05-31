#!/usr/bin/env python3
"""Local system CVE indicator scanner."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import platform

from lib.colors import Colors
from lib.local_checks import run_local_checks
from lib.reporter import ScanReport


def main() -> int:
    parser = argparse.ArgumentParser(description="Local CVE indicator detection")
    parser.add_argument("--output-dir", default="reports", help="Report output directory")
    args = parser.parse_args()

    host = platform.node() or "localhost"
    print(
        f"""{Colors.RED}
    ╔═══════════════════════════════════════════════════════════╗
    ║         🔴 LOCAL CVE INDICATOR SCANNER 🔴                ║
    ║      Physical / Local Access — Detection Only             ║
    ╚═══════════════════════════════════════════════════════════╝{Colors.END}
    Host: {Colors.BOLD}{host}{Colors.END}
    OS: {platform.system()} {platform.machine()}
    """
    )

    report = ScanReport.create(host)
    run_local_checks(report)
    report.print_summary()
    path = report.save(Path(args.output_dir))
    print(f"{Colors.CYAN}[*] Report saved to: {path}{Colors.END}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
