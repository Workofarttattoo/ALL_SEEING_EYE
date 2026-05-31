#!/usr/bin/env python3
"""Orchestrate ASE scan with optional external recon tools (tlsx, nuclei)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.colors import Colors


def _which(name: str) -> str | None:
    return shutil.which(name)


def run_cmd(cmd: list[str], desc: str) -> int:
    print(f"{Colors.CYAN}[*] {desc}{Colors.END}")
    print(f"    {' '.join(cmd)}")
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="2026 network recon orchestrator")
    parser.add_argument("target", nargs="?", help="Single target host or URL")
    parser.add_argument("--targets", help="File with URLs/hosts (one per line)")
    parser.add_argument("--output-dir", default="reports/network")
    parser.add_argument("--skip-ase", action="store_true", help="Skip ASE autorecon")
    parser.add_argument("--skip-external", action="store_true", help="Skip tlsx/nuclei")
    parser.add_argument("--aggressive", action="store_true")
    parser.add_argument("--shodan", action="store_true")
    args = parser.parse_args()

    if not args.target and not args.targets:
        parser.error("Provide target or --targets")

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    targets_file = out / "targets.txt"
    if args.targets:
        targets_file = Path(args.targets)
    elif args.target:
        targets_file.write_text(args.target.strip() + "\n")

    print(
        f"""{Colors.RED}
    ╔═══════════════════════════════════════════════════════════╗
    ║         Network Recon 2026 — ASE Orchestrator             ║
    ╚═══════════════════════════════════════════════════════════╝{Colors.END}
    """
    )

    if not args.skip_external:
        if _which("tlsx"):
            run_cmd(
                ["tlsx", "-l", str(targets_file), "-json", "-o", str(out / "tlsx.json")],
                "TLS/QUIC fingerprint (tlsx)",
            )
        else:
            print(f"{Colors.YELLOW}[!] tlsx not installed — run: bash scripts/install-recon-tools.sh{Colors.END}")

        if _which("nuclei"):
            run_cmd(
                [
                    "nuclei", "-l", str(targets_file),
                    "-tags", "misconfig,exposure",
                    "-json", "-o", str(out / "nuclei.json"),
                ],
                "Template scan (nuclei)",
            )
        else:
            print(f"{Colors.YELLOW}[!] nuclei not installed — run: bash scripts/install-recon-tools.sh{Colors.END}")

    if not args.skip_ase:
        targets = [ln.strip() for ln in targets_file.read_text().splitlines() if ln.strip()]
        for target in targets:
            cmd = [
                sys.executable,
                str(ROOT / "tools" / "autorecon.py"),
                target,
                "--output-dir",
                str(out / "ase"),
            ]
            if args.aggressive:
                cmd.append("--aggressive")
            if args.shodan:
                cmd.append("--shodan")
            run_cmd(cmd, f"ASE CVE fingerprint: {target}")

    summary = {
        "targets_file": str(targets_file),
        "output_dir": str(out),
        "tlsx": (out / "tlsx.json").exists(),
        "nuclei": (out / "nuclei.json").exists(),
    }
    (out / "network_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n{Colors.GREEN}[+] Done. Reports: {out}{Colors.END}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
