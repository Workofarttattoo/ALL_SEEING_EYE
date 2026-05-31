#!/usr/bin/env python3
"""
AURA — Automated Unified Reconnaissance Assistant
Subdomain enumeration, port discovery, and CVE fingerprinting (detection only).
"""

from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.colors import Colors
from lib.remote_checks import run_remote_checks
from lib.reporter import ScanReport
from lib.target import Target

DEFAULT_WORDLIST = ROOT / "data" / "wordlists" / "subdomains.txt"


def resolve_subdomain(domain: str) -> str | None:
    try:
        socket.gethostbyname(domain)
        return domain
    except OSError:
        return None


def enumerate_subdomains(base: str, wordlist: Path, workers: int = 20) -> list[str]:
    print(f"{Colors.CYAN}[*] Enumerating subdomains for {base}{Colors.END}")
    if not wordlist.exists():
        print(f"{Colors.YELLOW}[!] Wordlist missing: {wordlist}{Colors.END}")
        return []

    names = [line.strip() for line in wordlist.read_text().splitlines() if line.strip()]
    found: list[str] = []

    def task(sub: str) -> str | None:
        return resolve_subdomain(f"{sub}.{base}")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(task, sub): sub for sub in names}
        for future in as_completed(futures):
            hit = future.result()
            if hit:
                found.append(hit)
                print(f"{Colors.GREEN}[+] Found: {hit}{Colors.END}")

    return sorted(set(found))


def scan_ports_nmap(host: str, ports: str = "1-1000") -> list[int]:
    if not shutil.which("nmap"):
        print(f"{Colors.YELLOW}[!] nmap not installed — skipping port scan for {host}{Colors.END}")
        return quick_port_scan(host)

    print(f"{Colors.CYAN}[*] nmap port scan on {host} (ports {ports}){Colors.END}")
    cmd = ["nmap", "-p", ports, "-T4", "--open", "-oG", "-", host]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        open_ports: list[int] = []
        for line in result.stdout.splitlines():
            if "Ports:" not in line:
                continue
            segment = line.split("Ports:")[1].split("Ignored")[0]
            for part in segment.split(","):
                part = part.strip()
                if "/open/" in part:
                    open_ports.append(int(part.split("/")[0]))
        return sorted(open_ports)
    except (subprocess.TimeoutExpired, ValueError) as exc:
        print(f"{Colors.YELLOW}[!] nmap failed: {exc}{Colors.END}")
        return quick_port_scan(host)


def quick_port_scan(host: str, ports: list[int] | None = None) -> list[int]:
    ports = ports or [21, 22, 80, 443, 445, 3306, 3389, 8080, 8443]
    ip = socket.gethostbyname(host)
    open_ports: list[int] = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            if sock.connect_ex((ip, port)) == 0:
                open_ports.append(port)
        finally:
            sock.close()
    return open_ports


def service_fingerprint(host: str, port: int) -> str:
    if not shutil.which("nmap"):
        return ""
    cmd = ["nmap", "-sV", "-p", str(port), host]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        lines = [ln for ln in result.stdout.splitlines() if str(port) in ln and "open" in ln]
        return lines[0] if lines else ""
    except subprocess.TimeoutExpired:
        return ""


def check_legacy_cves(host: str, open_ports: list[int]) -> list[dict]:
    """Banner-based fingerprint hints — not exploitation."""
    vulns: list[dict] = []
    for port in open_ports:
        banner = service_fingerprint(host, port)
        if not banner:
            continue
        if "Apache" in banner and any(v in banner for v in ("2.4.48", "2.4.49", "2.4.50")):
            vulns.append(
                {
                    "host": host,
                    "port": port,
                    "service": banner,
                    "cve": "CVE-2021-41773",
                    "description": "Apache path traversal — verify patch level",
                }
            )
        if "OpenSSH" in banner:
            vulns.append(
                {
                    "host": host,
                    "port": port,
                    "service": banner,
                    "cve": "CVE-2023-25136",
                    "description": "OpenSSH — verify version for privilege escalation advisories",
                }
            )
    return vulns


def run_aura(
    target: str,
    *,
    wordlist: Path,
    ports: str,
    workers: int,
    skip_subdomains: bool,
    output_dir: Path,
) -> dict:
    base = target.replace("https://", "").replace("http://", "").split("/")[0]
    results: dict = {"target": base, "subdomains": [], "hosts": {}}

    hosts = [base]
    if not skip_subdomains:
        subs = enumerate_subdomains(base, wordlist, workers=workers)
        results["subdomains"] = subs
        hosts = sorted(set([base, *subs]))

    for host in hosts:
        host_ports = scan_ports_nmap(host, ports=ports)
        report = ScanReport.create(host)
        report.open_ports = host_ports

        t = Target.from_input(host)
        run_remote_checks(t, report, extended=True)
        legacy = check_legacy_cves(host, host_ports)

        results["hosts"][host] = {
            "open_ports": host_ports,
            "findings": [f.__dict__ if hasattr(f, "__dict__") else f for f in report.findings],
            "legacy_cve_hints": legacy,
        }
        report.save(output_dir)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="AURA unified recon assistant")
    parser.add_argument("--target", "-t", required=True, help="Base domain or host")
    parser.add_argument("--wordlist", default=str(DEFAULT_WORDLIST), help="Subdomain wordlist")
    parser.add_argument("--ports", default="1-1000", help="nmap port spec")
    parser.add_argument("--workers", type=int, default=20, help="Subdomain brute threads")
    parser.add_argument("--skip-subdomains", action="store_true")
    parser.add_argument("--output-dir", default="reports/aura")
    args = parser.parse_args()

    print(
        f"""{Colors.RED}
    ╔═══════════════════════════════════════════════════════════╗
    ║     AURA — Automated Unified Reconnaissance Assistant     ║
    ║              Detection / Fingerprinting Only                ║
    ╚═══════════════════════════════════════════════════════════╝{Colors.END}
    Target: {Colors.BOLD}{args.target}{Colors.END}
    """
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = run_aura(
        args.target,
        wordlist=Path(args.wordlist),
        ports=args.ports,
        workers=args.workers,
        skip_subdomains=args.skip_subdomains,
        output_dir=output_dir,
    )

    out = output_dir / f"aura_{results['target'].replace('.', '_')}.json"
    out.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n{Colors.CYAN}[*] AURA report: {out}{Colors.END}")
    total_findings = sum(len(h.get("findings", [])) for h in results["hosts"].values())
    print(f"{Colors.YELLOW}[*] Hosts: {len(results['hosts'])} | Findings: {total_findings}{Colors.END}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
