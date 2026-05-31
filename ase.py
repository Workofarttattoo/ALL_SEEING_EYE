#!/usr/bin/env python3
"""ALL_SEEING_EYE — unified CLI for authorized recon workflows."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
DOCS = ROOT / "docs"
DATA = ROOT / "data"


def cmd_handbook(args: argparse.Namespace) -> int:
    if getattr(args, "name", None):
        path = HANDBOOKS.get(args.name)
        if not path or not path.exists():
            print(f"Unknown handbook: {args.name}. Choose: red, purple, network")
            return 1
        print(path.read_text())
        return 0
    handbook = HANDBOOKS["red"]
    if not handbook.exists():
        print(f"Handbook not found at {handbook}")
        return 1
    print(handbook.read_text())
    return 0


PLAYBOOKS = {
    "blue": DOCS / "BLUE_TEAM_PLAYBOOK.md",
    "red": DOCS / "RED_TEAM_PLAYBOOK.md",
    "purple": DOCS / "PURPLE_TEAM_PLAYBOOK.md",
    "advanced": DOCS / "RED_TEAM_ADVANCED_PLAYBOOK.md",
}

HANDBOOKS = {
    "red": DOCS / "RED_TEAM_HANDBOOK.md",
    "purple": DOCS / "PURPLE_TEAM_HANDBOOK.md",
    "network": DOCS / "NETWORK_2026_GUIDE.md",
}

PURPLE_ROOT = ROOT / "purple"
SCRIPT_REFERENCE = PURPLE_ROOT / "script_reference.json"


def cmd_aura(args: argparse.Namespace) -> int:
    extra = ["--target", args.target, "--output-dir", args.output_dir]
    if args.skip_subdomains:
        extra.append("--skip-subdomains")
    if args.wordlist:
        extra.extend(["--wordlist", args.wordlist])
    if args.ports:
        extra.extend(["--ports", args.ports])
    return _run_tool("aura.py", extra)


def cmd_network(args: argparse.Namespace) -> int:
    extra: list[str] = []
    if args.targets:
        extra.extend(["--targets", args.targets])
    elif args.target:
        extra.append(args.target)
    else:
        print("Provide target or --targets")
        return 1
    extra.extend(["--output-dir", args.output_dir])
    if args.aggressive:
        extra.append("--aggressive")
    if args.shodan:
        extra.append("--shodan")
    if args.skip_external:
        extra.append("--skip-external")
    if args.skip_ase:
        extra.append("--skip-ase")
    return _run_tool("network_recon.py", extra)


def cmd_playbook(args: argparse.Namespace) -> int:
    path = PLAYBOOKS.get(args.team)
    if not path or not path.exists():
        print(f"Unknown playbook: {args.team}. Choose: blue, red, purple, advanced")
        return 1
    print(path.read_text())
    return 0


def cmd_scripts(args: argparse.Namespace) -> int:
    if not SCRIPT_REFERENCE.exists():
        print(f"Script reference not found: {SCRIPT_REFERENCE}")
        return 1
    ref = json.loads(SCRIPT_REFERENCE.read_text())

    if args.detection:
        print(f"{'NAME':<35} {'PHASE':<20} PATH")
        print("-" * 90)
        for item in ref.get("detection_assets", []):
            print(f"{item['name']:<35} {item.get('phase', ''):<20} {item['path']}")
        return 0

    phase_filter = args.phase
    print(f"{'SCRIPT':<18} {'PHASE(S)':<25} PATH")
    print("-" * 90)
    for item in ref.get("toolkit_scripts", []):
        phases = ", ".join(item.get("attack_phases", []))
        if phase_filter and phase_filter not in phases:
            continue
        print(f"{item['name']:<18} {phases:<25} {item['path']}")
        for cmd in item.get("key_commands", [])[:2]:
            print(f"  → {cmd}")
    print(f"\nDetection assets: {len(ref.get('detection_assets', []))} — use: ase scripts --detection")
    print(f"Full index: {SCRIPT_REFERENCE}")
    return 0


def cmd_list_cves(args: argparse.Namespace) -> int:
    payload = json.loads((DATA / "cves.json").read_text())
    section = payload.get(args.section, payload)
    if args.section != "all":
        for item in section:
            print(f"{item['id']:20} {item.get('cvss', 'N/A'):>4}  {item['target']}")
        return 0

    print("=== REMOTE ===")
    for item in payload["remote"]:
        print(f"{item['id']:20} {item['cvss']:>4}  {item['target']}")
    print("\n=== LOCAL ===")
    for item in payload["local"]:
        cvss = item.get("cvss")
        cvss_display = cvss if cvss is not None else "N/A"
        print(f"{item['id']:20} {str(cvss_display):>4}  {item['target']}")
    return 0


def _run_tool(script: str, extra: list[str]) -> int:
    path = TOOLS / script
    cmd = [sys.executable, str(path), *extra]
    return subprocess.call(cmd)


def cmd_scan(args: argparse.Namespace) -> int:
    extra = [args.target]
    if args.aggressive:
        extra.append("--aggressive")
    if args.shodan:
        extra.append("--shodan")
    extra.extend(["--output-dir", args.output_dir])
    return _run_tool("autorecon.py", extra)


def cmd_shodan(args: argparse.Namespace) -> int:
    extra: list[str] = [args.shodan_command, *args.shodan_args]
    if args.output:
        extra.extend(["--output", args.output])
    return _run_tool("shodan_recon.py", extra)


def cmd_local(args: argparse.Namespace) -> int:
    return _run_tool("local_detect.py", ["--output-dir", args.output_dir])


def cmd_remote(args: argparse.Namespace) -> int:
    extra = [args.target, "--output-dir", args.output_dir]
    if args.core_only:
        extra.append("--core-only")
    return _run_tool("remote_scan.py", extra)


def cmd_mass(args: argparse.Namespace) -> int:
    script = ROOT / "scripts" / "mass_scan.sh"
    if not script.exists():
        print(f"Missing script: {script}")
        return 1
    return subprocess.call(["bash", str(script), args.targets_file])


def cmd_rapid(args: argparse.Namespace) -> int:
    script = ROOT / "scripts" / "rapid_scan.sh"
    if not script.exists():
        print(f"Missing script: {script}")
        return 1
    return subprocess.call(["bash", str(script), args.targets_file])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ase",
        description="ALL_SEEING_EYE — authorized CVE recon toolkit",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    handbook = sub.add_parser("handbook", help="Print red or purple team handbook")
    handbook.add_argument(
        "name",
        nargs="?",
        choices=["red", "purple", "network"],
        help="Handbook to display (default: red CVE handbook)",
    )
    handbook.set_defaults(func=cmd_handbook)

    scripts = sub.add_parser("scripts", help="List toolkit scripts and detection assets")
    scripts.add_argument("--detection", action="store_true", help="Show detection rules only")
    scripts.add_argument(
        "--phase",
        help="Filter toolkit scripts by attack phase (e.g. reconnaissance)",
    )
    scripts.set_defaults(func=cmd_scripts)

    playbook = sub.add_parser("playbook", help="Print blue, red, or purple team playbook")
    playbook.add_argument(
        "team",
        choices=["blue", "red", "purple", "advanced"],
        help="Which playbook to display",
    )
    playbook.set_defaults(func=cmd_playbook)

    aura = sub.add_parser("aura", help="AURA unified recon (subdomains + ports + CVE scan)")
    aura.add_argument("target", help="Base domain or host")
    aura.add_argument("--wordlist", help="Subdomain wordlist path")
    aura.add_argument("--ports", default="1-1000", help="nmap port range")
    aura.add_argument("--skip-subdomains", action="store_true")
    aura.add_argument("--output-dir", default="reports/aura")
    aura.set_defaults(func=cmd_aura)

    network = sub.add_parser("network", help="2026 network recon (tlsx/nuclei + ASE)")
    network.add_argument("target", nargs="?", help="Single target")
    network.add_argument("--targets", help="Targets file")
    network.add_argument("--output-dir", default="reports/network")
    network.add_argument("--aggressive", action="store_true")
    network.add_argument("--shodan", action="store_true")
    network.add_argument("--skip-external", action="store_true")
    network.add_argument("--skip-ase", action="store_true")
    network.set_defaults(func=cmd_network)

    list_cves = sub.add_parser("cves", help="List tracked CVEs")
    list_cves.add_argument(
        "--section",
        choices=["all", "remote", "local"],
        default="all",
        help="CVE section to display",
    )
    list_cves.set_defaults(func=cmd_list_cves)

    scan = sub.add_parser("scan", help="Full autorecon against a target")
    scan.add_argument("target", help="URL, hostname, or IP")
    scan.add_argument("--aggressive", action="store_true", help="Extended remote checks")
    scan.add_argument("--shodan", action="store_true", help="Enrich scan with Shodan host intel")
    scan.add_argument("--output-dir", default="reports")
    scan.set_defaults(func=cmd_scan)

    shodan = sub.add_parser("shodan", help="Shodan intel: host, domain, hunt, search")
    shodan.add_argument(
        "shodan_command",
        choices=["info", "host", "domain", "hunt", "search", "dorks", "filters"],
        help="Shodan subcommand (pass extra args after --)",
    )
    shodan.add_argument("shodan_args", nargs="*", help="Arguments forwarded to shodan_recon.py")
    shodan.add_argument("--output", "-o", help="Output file forwarded when supported")
    shodan.set_defaults(func=cmd_shodan)

    local = sub.add_parser("local", help="Local system indicator scan")
    local.add_argument("--output-dir", default="reports")
    local.set_defaults(func=cmd_local)

    remote = sub.add_parser("remote", help="Remote-only fingerprint scan")
    remote.add_argument("target", help="URL, hostname, or IP")
    remote.add_argument("--core-only", action="store_true")
    remote.add_argument("--output-dir", default="reports")
    remote.set_defaults(func=cmd_remote)

    mass = sub.add_parser("mass", help="Bulk scan targets from a file")
    mass.add_argument("targets_file", help="Newline-delimited targets file")
    mass.set_defaults(func=cmd_mass)

    rapid = sub.add_parser("rapid", help="Rapid remote CVE identification")
    rapid.add_argument("targets_file", help="Newline-delimited targets file")
    rapid.set_defaults(func=cmd_rapid)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
