"""Shodan API client — host intel, search, DNS, and CVE dork hunting."""

from __future__ import annotations

import json
import os
import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from lib.colors import Colors

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DORKS_FILE = DATA_DIR / "shodan_dorks.json"


class ShodanNotConfiguredError(RuntimeError):
    pass


class ShodanClient:
    """Thin wrapper around the official shodan Python library."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("SHODAN_API_KEY", "").strip()
        if not self.api_key:
            raise ShodanNotConfiguredError(
                "SHODAN_API_KEY not set. Get a key at https://account.shodan.io "
                "and export SHODAN_API_KEY or add it to .env"
            )
        try:
            import shodan
        except ImportError as exc:
            raise RuntimeError("Install shodan: pip install shodan") from exc

        self._api = shodan.Shodan(self.api_key)

    @classmethod
    def try_create(cls) -> "ShodanClient | None":
        try:
            return cls()
        except (ShodanNotConfiguredError, RuntimeError):
            return None

    def info(self) -> dict[str, Any]:
        return self._api.info()

    def host(self, ip: str, history: bool = False) -> dict[str, Any]:
        return self._api.host(ip, history=history)

    def search(
        self,
        query: str,
        page: int = 1,
        facets: str | None = None,
        minify: bool = True,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"query": query, "page": page, "minify": minify}
        if facets:
            kwargs["facets"] = facets
        return self._api.search(**kwargs)

    def count(self, query: str, facets: str | None = None) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"query": query}
        if facets:
            kwargs["facets"] = facets
        return self._api.count(**kwargs)

    def search_cursor(self, query: str) -> Iterator[dict[str, Any]]:
        return self._api.search_cursor(query)

    def dns_resolve(self, hostnames: list[str]) -> dict[str, str]:
        return self._api.dns.resolve(",".join(hostnames))

    def dns_reverse(self, ips: list[str]) -> dict[str, list[str]]:
        return self._api.dns.reverse(",".join(ips))

    def dns_domain(self, domain: str, history: bool = False) -> dict[str, Any]:
        return self._api.dns.domain_info(domain, history=history)

    def filters(self) -> list[str]:
        return self._api.search_filters()

    def load_dorks(self) -> dict[str, Any]:
        return json.loads(DORKS_FILE.read_text())


@dataclass
class ShodanMatch:
    ip: str
    port: int
    product: str | None
    org: str | None
    hostnames: list[str]
    query: str
    cve: str
    banner_preview: str
    vulns: list[str] = field(default_factory=list)

    @classmethod
    def from_banner(cls, match: dict[str, Any], *, query: str, cve: str) -> "ShodanMatch":
        vulns = match.get("vulns") or []
        if isinstance(vulns, dict):
            vulns = list(vulns.keys())
        banner = match.get("data") or match.get("http", {}).get("html") or ""
        return cls(
            ip=match.get("ip_str", ""),
            port=int(match.get("port", 0)),
            product=match.get("product"),
            org=match.get("org"),
            hostnames=match.get("hostnames") or [],
            query=query,
            cve=cve,
            banner_preview=str(banner)[:200],
            vulns=vulns,
        )


def resolve_to_ip(value: str) -> str:
    value = value.replace("http://", "").replace("https://", "").split("/")[0]
    if ":" in value and not value.count(":") > 1:
        value = value.split(":")[0]
    try:
        socket.inet_aton(value)
        return value
    except OSError:
        return socket.gethostbyname(value)


def host_to_findings(host_data: dict[str, Any], target: str) -> list[dict[str, Any]]:
    """Translate Shodan host profile into ASE finding dicts."""
    findings: list[dict[str, Any]] = []

    ports = host_data.get("ports") or []
    if ports:
        findings.append(
            {
                "cve": "SHODAN-PORTS",
                "confidence": "INFO",
                "notes": f"Shodan indexed ports: {sorted(ports)}",
                "category": "shodan",
                "extra": {"ports": ports},
            }
        )

    for vuln in host_data.get("vulns") or []:
        findings.append(
            {
                "cve": vuln if vuln.startswith("CVE-") else f"CVE-{vuln}",
                "confidence": "HIGH",
                "notes": "Shodan vuln tag on host — verify patch level",
                "category": "shodan",
            }
        )

    for tag in host_data.get("tags") or []:
        findings.append(
            {
                "cve": f"SHODAN-TAG-{tag.upper()}",
                "confidence": "INFO",
                "notes": f"Shodan tag: {tag}",
                "category": "shodan",
            }
        )

    for banner in host_data.get("data") or []:
        product = banner.get("product") or ""
        port = banner.get("port")
        data = banner.get("data") or ""
        http = banner.get("http") or {}
        title = http.get("title") or ""

        fingerprint = " ".join(filter(None, [product, title, data[:120]])).lower()
        cve_hints = _match_fingerprint_to_cves(fingerprint, port)
        for cve_id, note in cve_hints:
            findings.append(
                {
                    "cve": cve_id,
                    "confidence": "MEDIUM",
                    "notes": f"Shodan banner match: {note}",
                    "category": "shodan",
                    "port": port,
                    "banner": data[:200] if data else None,
                    "extra": {"product": product, "http_title": title},
                }
            )

    if host_data.get("org"):
        findings.append(
            {
                "cve": "SHODAN-ORG",
                "confidence": "INFO",
                "notes": f"Org: {host_data['org']} | ISP: {host_data.get('isp', 'n/a')}",
                "category": "shodan",
                "extra": {
                    "org": host_data.get("org"),
                    "isp": host_data.get("isp"),
                    "asn": host_data.get("asn"),
                },
            }
        )

    if not findings:
        findings.append(
            {
                "cve": "SHODAN-HOST",
                "confidence": "INFO",
                "notes": f"Shodan has indexed {target} but no CVE-aligned banners matched",
                "category": "shodan",
            }
        )

    return findings


def _match_fingerprint_to_cves(fingerprint: str, port: int | None) -> list[tuple[str, str]]:
    rules: list[tuple[list[str], str, str]] = [
        (["sap", "netweaver", "visual composer"], "CVE-2025-31324", "SAP NetWeaver"),
        (["big-ip", "f5", "tmui"], "CVE-2025-53521", "F5 BIG-IP"),
        (["next.js", "__next", "/_next"], "CVE-2025-66478", "Next.js"),
        (["mongodb"], "CVE-2025-14847", "MongoDB"),
        (["showdoc"], "CVE-2025-0520", "ShowDoc"),
        (["metinfo"], "CVE-2026-29014", "MetInfo CMS"),
        (["flowise"], "CVE-2025-59528", "Flowise AI"),
        (["n8n"], "CVE-2026-27493", "n8n"),
        (["oracle identity", "oracleidentitymanager", "/oim/"], "CVE-2026-21992", "Oracle IEM"),
        (["identity services engine", " cisco ise"], "CISCO-ISE-RCE", "Cisco ISE"),
        (["firepower management", "fmc"], "CISCO-FMC-RCE", "Cisco FMC"),
        (["erlang"], "CVE-2025-32433", "Erlang SSH"),
    ]
    hits: list[tuple[str, str]] = []
    for needles, cve, label in rules:
        if any(n in fingerprint for n in needles):
            hits.append((cve, label))
    if port == 27017 and not any(h[0] == "CVE-2025-14847" for h in hits):
        hits.append(("CVE-2025-14847", "MongoDB port 27017"))
    return hits


def hunt_cve(
    client: ShodanClient,
    cve: str | None = None,
    scope: str | None = None,
    limit: int = 10,
    count_only: bool = False,
) -> dict[str, Any]:
    """Run Shodan dork catalog, optionally scoped to org/net/hostname."""
    catalog = client.load_dorks()
    dorks = catalog["dorks"]
    if cve:
        dorks = [d for d in dorks if d["cve"].upper() == cve.upper()]
        if not dorks:
            raise ValueError(f"No Shodan dorks configured for {cve}")

    results: dict[str, Any] = {"queries": [], "matches": [], "total_hits": 0}

    for entry in dorks:
        for query in entry["queries"]:
            scoped = f"{query} {scope}".strip() if scope else query
            facets = ",".join(entry.get("facets") or [])

            print(f"{Colors.CYAN}[*] Shodan: {scoped}{Colors.END}")

            if count_only:
                data = client.count(scoped, facets=facets or None)
                hit_count = data.get("total", 0)
                results["queries"].append(
                    {"cve": entry["cve"], "query": scoped, "total": hit_count, "facets": data.get("facets")}
                )
                results["total_hits"] += hit_count
                print(f"{Colors.YELLOW}    → {hit_count:,} hosts{Colors.END}")
                continue

            data = client.search(scoped, facets=facets or None)
            total = data.get("total", 0)
            results["queries"].append({"cve": entry["cve"], "query": scoped, "total": total})
            results["total_hits"] += total
            print(f"{Colors.YELLOW}    → {total:,} total | showing {min(limit, len(data.get('matches', [])))}{Colors.END}")

            for match in data.get("matches", [])[:limit]:
                sm = ShodanMatch.from_banner(match, query=scoped, cve=entry["cve"])
                results["matches"].append(sm.__dict__)

                vuln_str = f" vulns={sm.vulns}" if sm.vulns else ""
                host_str = sm.hostnames[0] if sm.hostnames else sm.ip
                print(
                    f"{Colors.RED}    [!] {sm.cve} {host_str}:{sm.port} "
                    f"({sm.org or 'unknown org'}){vuln_str}{Colors.END}"
                )

    return results


def print_host_summary(host_data: dict[str, Any]) -> None:
    print(f"\n{Colors.BOLD}Shodan Host Profile{Colors.END}")
    print(f"  IP:       {host_data.get('ip_str')}")
    print(f"  Org:      {host_data.get('org', 'n/a')}")
    print(f"  ISP:      {host_data.get('isp', 'n/a')}")
    print(f"  ASN:      {host_data.get('asn', 'n/a')}")
    print(f"  OS:       {host_data.get('os', 'n/a')}")
    print(f"  Ports:    {sorted(host_data.get('ports') or [])}")
    print(f"  Hostnames:{', '.join(host_data.get('hostnames') or []) or 'n/a'}")
    print(f"  Tags:     {', '.join(host_data.get('tags') or []) or 'n/a'}")
    vulns = host_data.get("vulns") or []
    if vulns:
        print(f"  {Colors.RED}Vulns:    {', '.join(vulns)}{Colors.END}")
    loc = host_data.get("location") or {}
    if loc:
        print(
            f"  Location: {loc.get('city', '')}, {loc.get('country_name', '')} "
            f"({loc.get('country_code', '')})"
        )
    print(f"\n{Colors.CYAN}Banners:{Colors.END}")
    for item in host_data.get("data") or []:
        print(f"  Port {item.get('port')} | {item.get('product') or 'unknown product'}")
        preview = (item.get("data") or "")[:160].replace("\n", " ")
        if preview:
            print(f"    {preview}")
