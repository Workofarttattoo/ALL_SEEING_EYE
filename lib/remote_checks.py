"""Remote CVE fingerprinting checks — detection only, no exploitation."""

from __future__ import annotations

import socket
import threading
from typing import Callable

import requests

from lib.colors import Colors
from lib.reporter import Finding, ScanReport
from lib.target import Target

requests.packages.urllib3.disable_warnings()


CheckFn = Callable[[Target, ScanReport], None]

COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995,
    1723, 3306, 3389, 5432, 5900, 5901, 6379, 8080, 8443,
    9200, 9300, 27017, 50000,
]

MONGO_PORTS = [27017, 27018, 27019, 28017]


def _get(session: requests.Session, url: str, **kwargs) -> requests.Response | None:
    try:
        return session.get(url, timeout=kwargs.pop("timeout", 10), verify=False, **kwargs)
    except requests.RequestException:
        return None


def port_scan_quick(target: Target, report: ScanReport) -> list[int]:
    print(f"\n{Colors.CYAN}[*] Running quick port scan...{Colors.END}")
    ip = target.resolve()
    open_ports: list[int] = []
    lock = threading.Lock()

    def check_port(port: int) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            if sock.connect_ex((ip, port)) == 0:
                with lock:
                    open_ports.append(port)
                print(f"{Colors.GREEN}[+] Port {port} OPEN{Colors.END}")
        finally:
            sock.close()

    threads = [threading.Thread(target=check_port, args=(p,)) for p in COMMON_PORTS]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    report.open_ports = sorted(open_ports)
    return report.open_ports


def check_sap_cve_2025_31324(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2025-31324 (SAP NetWeaver RCE)...{Colors.END}")
    session = requests.Session()
    paths = [
        "/VisualComposer/VCFramework.wdvc",
        "/VCFramework.wdvc",
        "/visualcomposer/VCFramework.wdvc",
        "/nwbc/VCFramework.wdvc",
    ]
    markers = ("sap", "visualcomposer", "vcframework")

    for path in paths:
        url = target.url(path)
        response = _get(session, url, allow_redirects=False)
        if not response:
            continue
        body = response.text.lower()
        if response.status_code in (200, 401, 403, 500) and any(m in body for m in markers):
            print(f"{Colors.RED}[!] POTENTIAL SAP TARGET: {url}{Colors.END}")
            report.add(
                Finding(
                    cve="CVE-2025-31324",
                    confidence="HIGH",
                    notes="SAP Visual Composer detected — verify patch level",
                    url=url,
                )
            )
            upload_url = f"{url.rstrip('/')}/upload"
            upload_resp = _get(session, upload_url, timeout=5)
            if upload_resp and upload_resp.status_code == 200:
                print(f"{Colors.RED}[!!!] Upload endpoint responsive: {upload_url}{Colors.END}")


def check_react_nextjs(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2025-55182/66478 (React/Next.js)...{Colors.END}")
    session = requests.Session()
    response = _get(session, target.url())
    if not response:
        return

    for header in ("x-powered-by", "server", "via"):
        value = response.headers.get(header, "").lower()
        if "next.js" in value or "nextjs" in value:
            print(f"{Colors.RED}[!] Next.js detected in header: {header}{Colors.END}")
            report.add(
                Finding(
                    cve="CVE-2025-66478",
                    confidence="MEDIUM",
                    notes="Next.js framework detected — review SSRF/RCE advisories",
                )
            )

    body = response.text.lower()
    if "reactroot" in body or "__next" in body:
        print(f"{Colors.YELLOW}[*] React/Next.js body indicators present{Colors.END}")

    for path in (
        "/_next/static/",
        "/__nextjs_original-stack-frame",
        "/_next/image",
        "/api/hello",
        "/api/health",
    ):
        endpoint = target.url(path)
        hit = _get(session, endpoint, timeout=5)
        if hit and hit.status_code == 200:
            print(f"{Colors.RED}[!] Next.js endpoint found: {path}{Colors.END}")


def check_f5_bigip(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2025-53521 (F5 BIG-IP RCE)...{Colors.END}")
    session = requests.Session()
    url = target.url("/tmui/login.jsp", use_https=True)
    response = _get(session, url)
    if response and any(x in response.text.lower() for x in ("f5", "big-ip")):
        print(f"{Colors.RED}[!] F5 BIG-IP detected{Colors.END}")
        report.add(
            Finding(
                cve="CVE-2025-53521",
                confidence="HIGH",
                notes="F5 BIG-IP login surface detected — review iControl REST exposure",
                url=url,
            )
        )


def check_mongodb(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2025-14847 (MongoDB MongoBleed)...{Colors.END}")
    ip = target.resolve()
    for port in MONGO_PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        try:
            if sock.connect_ex((ip, port)) == 0:
                print(f"{Colors.RED}[!] MongoDB port OPEN: {port}{Colors.END}")
                report.add(
                    Finding(
                        cve="CVE-2025-14847",
                        confidence="HIGH",
                        notes="MongoDB port exposed — verify auth and patch level",
                        port=port,
                    )
                )
        finally:
            sock.close()


def check_metinfo(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2026-29014 (MetInfo CMS)...{Colors.END}")
    response = _get(requests.Session(), target.url())
    if response and ("metinfo" in response.text.lower() or 'content="metinfo"' in response.text.lower()):
        print(f"{Colors.RED}[!] MetInfo CMS detected{Colors.END}")
        report.add(
            Finding(
                cve="CVE-2026-29014",
                confidence="HIGH",
                notes="MetInfo CMS fingerprint — versions 7.9-8.1 affected",
            )
        )


def check_showdoc(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2025-0520 (ShowDoc)...{Colors.END}")
    url = target.url("/server/index.php")
    response = _get(requests.Session(), url)
    if response and "showdoc" in response.text.lower():
        print(f"{Colors.RED}[!] ShowDoc detected{Colors.END}")
        report.add(
            Finding(
                cve="CVE-2025-0520",
                confidence="HIGH",
                notes="ShowDoc detected — versions below 2.8.7 affected",
                url=url,
            )
        )


def check_erlang_ssh(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2025-32433 (Erlang SSH)...{Colors.END}")
    ip = target.resolve()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((ip, 22))
        banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
        print(f"{Colors.YELLOW}[*] SSH Banner: {banner}{Colors.END}")
        if "erlang" in banner.lower() or banner.startswith("SSH-2.0"):
            report.add(
                Finding(
                    cve="CVE-2025-32433",
                    confidence="MEDIUM",
                    notes="SSH service exposed — verify Erlang SSH library version",
                    port=22,
                    banner=banner,
                )
            )
    except OSError:
        pass
    finally:
        sock.close()


def check_cisco_rest(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2026-20223 (Cisco REST API)...{Colors.END}")
    session = requests.Session()
    for path in ("/api/v1/auth", "/api/v1/system", "/restconf/", "/.well-known/host-meta"):
        url = target.url(path, use_https=True)
        response = _get(session, url, timeout=5)
        if not response:
            continue
        haystack = f"{response.text} {response.headers}".lower()
        if "cisco" in haystack:
            print(f"{Colors.RED}[!] Cisco REST surface detected: {path}{Colors.END}")
            report.add(
                Finding(
                    cve="CVE-2026-20223",
                    confidence="MEDIUM",
                    notes="Cisco REST API fingerprint — verify auth bypass patches",
                    url=url,
                )
            )
            break


def check_adobe_vectors(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2026-34621 (Adobe Acrobat vectors)...{Colors.END}")
    session = requests.Session()
    for path in ("/upload", "/documents/upload", "/api/upload", "/file/upload"):
        url = target.url(path)
        try:
            response = session.options(url, timeout=5, verify=False)
            if response.status_code == 200:
                print(f"{Colors.YELLOW}[*] Upload endpoint found: {path}{Colors.END}")
                report.add(
                    Finding(
                        cve="CVE-2026-34621",
                        confidence="LOW",
                        notes="PDF upload surface — Adobe RCE typically needs user interaction",
                        url=url,
                    )
                )
        except requests.RequestException:
            continue


def check_flowise(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2025-59528 (Flowise AI)...{Colors.END}")
    url = target.url("/api/v1/chatflows")
    response = _get(requests.Session(), url)
    if response and response.status_code == 200 and "flowise" in response.text.lower():
        print(f"{Colors.RED}[!] Flowise AI detected{Colors.END}")
        report.add(
            Finding(
                cve="CVE-2025-59528",
                confidence="HIGH",
                notes="Flowise AI API exposed — review workflow RCE advisories",
                url=url,
            )
        )


def check_oracle_oim(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking CVE-2026-21992 (Oracle Identity Manager)...{Colors.END}")
    session = requests.Session()
    for path in (
        "/oim/faces/adf.task-flow",
        "/oim/faces/OracleIdentityManager",
        "/oim/identity/faces/adf.task-flow",
    ):
        url = target.url(path, use_https=True)
        response = _get(session, url, timeout=10)
        if response and any(x in response.text.lower() for x in ("oracle.identity", "adffaces", "oracle")):
            print(f"{Colors.RED}[!] Oracle Identity Manager surface: {path}{Colors.END}")
            report.add(
                Finding(
                    cve="CVE-2026-21992",
                    confidence="HIGH",
                    notes="Oracle IEM/ADF surface detected — verify pre-auth RCE patches",
                    url=url,
                )
            )
            break


def check_n8n(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking n8n CVEs (27577, 27493, 21858)...{Colors.END}")
    session = requests.Session()
    health = _get(session, target.url("/healthz"))
    if not health or "n8n" not in health.text.lower():
        return

    print(f"{Colors.RED}[!] n8n instance detected{Colors.END}")
    report.add(
        Finding(
            cve="CVE-2026-27493",
            confidence="HIGH",
            notes="n8n health endpoint exposed — review form/webhook RCE advisories",
            url=target.url("/healthz"),
        )
    )

    for path in ("/form", "/form/", "/webhook", "/webhook/"):
        url = target.url(path)
        response = _get(session, url, timeout=5)
        if response and response.status_code in (200, 405):
            report.add(
                Finding(
                    cve="CVE-2026-21858",
                    confidence="MEDIUM",
                    notes=f"n8n public workflow surface at {path}",
                    url=url,
                )
            )


def check_cisco_ise(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking Cisco ISE unauthenticated RCE indicators...{Colors.END}")
    session = requests.Session()
    for path in ("/admin/", "/ise/", "/setup/", "/ers/"):
        url = target.url(path, use_https=True)
        response = _get(session, url, timeout=10)
        if response and "cisco" in response.text.lower() and "ise" in response.text.lower():
            print(f"{Colors.RED}[!] Cisco ISE detected: {path}{Colors.END}")
            report.add(
                Finding(
                    cve="CISCO-ISE-RCE",
                    confidence="HIGH",
                    notes="Cisco ISE admin surface detected",
                    url=url,
                )
            )
            break


def check_cisco_fmc(target: Target, report: ScanReport) -> None:
    print(f"\n{Colors.CYAN}[*] Checking Cisco FMC RCE indicators...{Colors.END}")
    session = requests.Session()
    for path in ("/api/fmc_config/", "/api/v1/", "/ui/"):
        url = target.url(path, use_https=True)
        response = _get(session, url, timeout=10)
        if not response:
            continue
        haystack = f"{response.text} {response.headers}".lower()
        if "cisco" in haystack or "fmc" in haystack:
            print(f"{Colors.RED}[!] Cisco FMC surface detected: {path}{Colors.END}")
            report.add(
                Finding(
                    cve="CISCO-FMC-RCE",
                    confidence="MEDIUM",
                    notes="Cisco FMC API/UI detected — verify deserialization patches",
                    url=url,
                )
            )
            break


REMOTE_CHECKS: list[tuple[str, CheckFn]] = [
    ("core", check_sap_cve_2025_31324),
    ("core", check_react_nextjs),
    ("core", check_f5_bigip),
    ("core", check_mongodb),
    ("core", check_metinfo),
    ("core", check_showdoc),
    ("core", check_erlang_ssh),
    ("core", check_cisco_rest),
    ("core", check_adobe_vectors),
    ("core", check_flowise),
    ("extended", check_oracle_oim),
    ("extended", check_n8n),
    ("extended", check_cisco_ise),
    ("extended", check_cisco_fmc),
]


def run_remote_checks(target: Target, report: ScanReport, extended: bool = True) -> None:
    for tier, check in REMOTE_CHECKS:
        if tier == "extended" and not extended:
            continue
        check(target, report)
