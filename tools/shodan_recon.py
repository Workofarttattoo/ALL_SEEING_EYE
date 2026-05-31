#!/usr/bin/env python3
"""Shodan-powered recon — host intel, DNS, CVE dork hunting."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.colors import Colors
from lib.shodan_client import (
    ShodanClient,
    ShodanNotConfiguredError,
    hunt_cve,
    print_host_summary,
    resolve_to_ip,
)


def cmd_info(client: ShodanClient) -> int:
    info = client.info()
    print(f"{Colors.BOLD}Shodan API Account{Colors.END}")
    for key in ("plan", "query_credits", "scan_credits", "monitored_ips"):
        if key in info:
            print(f"  {key}: {info[key]}")
    return 0


def cmd_host(args: argparse.Namespace, client: ShodanClient) -> int:
    ip = resolve_to_ip(args.target)
    host_data = client.host(ip, history=args.history)
    print_host_summary(host_data)
    if args.output:
        Path(args.output).write_text(json.dumps(host_data, indent=2, default=str))
        print(f"\n{Colors.CYAN}[*] Saved to {args.output}{Colors.END}")
    return 0


def cmd_domain(args: argparse.Namespace, client: ShodanClient) -> int:
    data = client.dns_domain(args.domain, history=args.history)
    print(f"\n{Colors.BOLD}Shodan DNS: {args.domain}{Colors.END}")
    print(f"  Tags: {', '.join(data.get('tags') or []) or 'none'}")
    subs = data.get("subdomains") or []
    print(f"  Subdomains ({len(subs)}):")
    for sub in subs[: args.limit]:
        print(f"    {sub}.{args.domain}")
    if len(subs) > args.limit:
        print(f"    ... and {len(subs) - args.limit} more (use --limit)")

    records = data.get("data") or []
    if records:
        print(f"\n{Colors.CYAN}DNS Records (sample):{Colors.END}")
        for rec in records[: args.limit]:
            print(f"  {rec.get('subdomain', '@')}.{args.domain} {rec.get('type')} → {rec.get('value')}")

    if args.output:
        Path(args.output).write_text(json.dumps(data, indent=2, default=str))
    return 0


def cmd_hunt(args: argparse.Namespace, client: ShodanClient) -> int:
    scope = None
    if args.org:
        scope = f'org:"{args.org}"'
    elif args.net:
        scope = f"net:{args.net}"
    elif args.hostname:
        scope = f"hostname:{args.hostname}"
    elif args.country:
        scope = f"country:{args.country}"

    results = hunt_cve(
        client,
        cve=args.cve,
        scope=scope,
        limit=args.limit,
        count_only=args.count_only,
    )

    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2, default=str))
        print(f"\n{Colors.CYAN}[*] Saved to {args.output}{Colors.END}")
    return 0


def cmd_search(args: argparse.Namespace, client: ShodanClient) -> int:
    if args.count_only:
        data = client.count(args.query, facets=args.facets)
        print(json.dumps(data, indent=2))
        return 0

    data = client.search(args.query, page=args.page, facets=args.facets)
    print(f"Total: {data.get('total', 0):,}")
    for match in data.get("matches", [])[: args.limit]:
        ip = match.get("ip_str")
        port = match.get("port")
        org = match.get("org", "unknown")
        product = match.get("product", "")
        print(f"  {ip}:{port} {org} {product}")
    if args.output:
        Path(args.output).write_text(json.dumps(data, indent=2, default=str))
    return 0


def cmd_dorks(_: argparse.Namespace, client: ShodanClient | None = None) -> int:
    catalog = json.loads((Path(__file__).resolve().parents[1] / "data" / "shodan_dorks.json").read_text())
    print(f"{Colors.BOLD}CVE → Shodan Dork Catalog{Colors.END}\n")
    for entry in catalog["dorks"]:
        print(f"{Colors.YELLOW}{entry['cve']}{Colors.END} — {entry['target']}")
        for query in entry["queries"]:
            print(f"  • {query}")
        print()
    return 0


def cmd_filters(_: argparse.Namespace, client: ShodanClient) -> int:
    filters = client.filters()
    print(f"{Colors.BOLD}Shodan search filters ({len(filters)}){Colors.END}\n")
    for name in sorted(filters):
        print(f"  {name}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Shodan recon for ALL_SEEING_EYE")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("info", help="Show API account credits/plan")

    host = sub.add_parser("host", help="Full Shodan host profile for IP/domain")
    host.add_argument("target")
    host.add_argument("--history", action="store_true", help="Include historical banners")
    host.add_argument("--output", "-o", help="Save JSON output")

    domain = sub.add_parser("domain", help="DNS/subdomain intel from Shodan")
    domain.add_argument("domain")
    domain.add_argument("--history", action="store_true")
    domain.add_argument("--limit", type=int, default=50)
    domain.add_argument("--output", "-o")

    hunt = sub.add_parser("hunt", help="Run CVE dork catalog against Shodan index")
    hunt.add_argument("--cve", help="Single CVE from catalog (default: all)")
    hunt.add_argument("--org", help='Scope to org, e.g. "Acme Corp"')
    hunt.add_argument("--net", help="Scope to CIDR, e.g. 192.168.1.0/24")
    hunt.add_argument("--hostname", help="Scope to hostname")
    hunt.add_argument("--country", help="Scope to country code, e.g. US")
    hunt.add_argument("--limit", type=int, default=10, help="Max matches per query")
    hunt.add_argument("--count-only", action="store_true", help="Count hits only (saves credits)")
    hunt.add_argument("--output", "-o")

    search = sub.add_parser("search", help="Raw Shodan search query")
    search.add_argument("query")
    search.add_argument("--facets", help="Comma-separated facets, e.g. org,country")
    search.add_argument("--page", type=int, default=1)
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--count-only", action="store_true")
    search.add_argument("--output", "-o")

    sub.add_parser("dorks", help="List CVE-to-Shodan query mappings")
    sub.add_parser("filters", help="List available Shodan search filters")

    args = parser.parse_args()

    if args.command == "dorks":
        return cmd_dorks(args)

    try:
        client = ShodanClient()
    except ShodanNotConfiguredError as exc:
        print(f"{Colors.RED}[-] {exc}{Colors.END}")
        return 1
    except RuntimeError as exc:
        print(f"{Colors.RED}[-] {exc}{Colors.END}")
        return 1

    handlers = {
        "info": lambda: cmd_info(client),
        "host": lambda: cmd_host(args, client),
        "domain": lambda: cmd_domain(args, client),
        "hunt": lambda: cmd_hunt(args, client),
        "search": lambda: cmd_search(args, client),
        "filters": lambda: cmd_filters(args, client),
    }
    return handlers[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
