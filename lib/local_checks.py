"""Local / physical CVE indicator checks — detection only."""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

from lib.colors import Colors
from lib.reporter import Finding, ScanReport


def _run(cmd: list[str], timeout: int = 10) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return 1, "", str(exc)


def check_linux_kernel_surface(report: ScanReport) -> None:
    if platform.system() != "Linux":
        return

    print(f"\n{Colors.CYAN}[*] Checking Linux kernel LPE indicators...{Colors.END}")
    _, release, _ = _run(["uname", "-r"])
    release = release.strip()
    print(f"{Colors.YELLOW}[*] Kernel: {release}{Colors.END}")

    for module in ("af_alg", "xfrm4", "rxrpc"):
        mod_path = Path(f"/sys/module/{module}")
        if mod_path.exists():
            report.add(
                Finding(
                    cve="CVE-2026-31431" if module == "af_alg" else "CVE-2026-43500",
                    category="local",
                    confidence="LOW",
                    notes=f"Kernel module {module} present — verify patch level for {release}",
                    extra={"kernel": release, "module": module},
                )
            )


def check_azure_arc_windows(report: ScanReport) -> None:
    if platform.system() != "Windows":
        return

    print(f"\n{Colors.CYAN}[*] Checking CVE-2026-26117 (Azure Arc)...{Colors.END}")
    paths = [
        Path(r"C:\Program Files\AzureConnectedMachineAgent"),
        Path(r"C:\ProgramData\AzureConnectedMachineAgent"),
    ]
    for path in paths:
        if path.exists():
            print(f"{Colors.RED}[!] Azure Arc agent path found: {path}{Colors.END}")
            report.add(
                Finding(
                    cve="CVE-2026-26117",
                    category="local",
                    confidence="MEDIUM",
                    notes="Azure Arc agent installed — audit agent directory ACLs",
                    extra={"path": str(path)},
                )
            )


def check_windows_cloud_filter(report: ScanReport) -> None:
    if platform.system() != "Windows":
        return

    print(f"\n{Colors.CYAN}[*] Checking CVE-2025-62221 (Cloud Filter / MiniPlasma)...{Colors.END}")
    cldapi = Path(r"C:\Windows\System32\cldapi.dll")
    if cldapi.exists():
        print(f"{Colors.YELLOW}[*] cldapi.dll present{Colors.END}")
        report.add(
            Finding(
                cve="CVE-2025-62221",
                category="local",
                confidence="LOW",
                notes="Cloud Filter driver present — verify Windows patch level",
                extra={"component": str(cldapi)},
            )
        )


def check_bitlocker_winre(report: ScanReport) -> None:
    if platform.system() != "Windows":
        return

    print(f"\n{Colors.CYAN}[*] Checking BitLocker / WinRE exposure (YellowKey)...{Colors.END}")
    code, stdout, _ = _run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "(Get-BitLockerVolume -ErrorAction SilentlyContinue | "
            "Select-Object -ExpandProperty ProtectionStatus) -join ','",
        ]
    )
    if code == 0 and stdout.strip():
        print(f"{Colors.YELLOW}[*] BitLocker status: {stdout.strip()}{Colors.END}")
        report.add(
            Finding(
                cve="YELLOWKEY",
                category="local",
                confidence="INFO",
                notes="BitLocker configured — physical WinRE/USB attacks require boot access",
                extra={"protection_status": stdout.strip()},
            )
        )


def check_windows_service_hijack_surface(report: ScanReport) -> None:
    if platform.system() != "Windows":
        return

    print(f"\n{Colors.CYAN}[*] Checking CVE-2025-54100 service hijack surface...{Colors.END}")
    ps = (
        "Get-CimInstance Win32_Service | "
        "Where-Object { $_.PathName -match 'Users|Temp' } | "
        "Select-Object -First 5 Name, PathName | ConvertTo-Json"
    )
    code, stdout, _ = _run(["powershell", "-NoProfile", "-Command", ps], timeout=20)
    if code == 0 and stdout.strip() and stdout.strip() != "":
        report.add(
            Finding(
                cve="CVE-2025-54100",
                category="local",
                confidence="LOW",
                notes="Review writable service binary paths for local privilege escalation",
                extra={"sample": stdout.strip()[:500]},
            )
        )


def check_local_privileges(report: ScanReport) -> None:
    if platform.system() == "Windows":
        code, stdout, _ = _run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "[bool](([Security.Principal.WindowsPrincipal]"
                "[Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole("
                "[Security.Principal.WindowsBuiltInRole]::Administrator))",
            ]
        )
        elevated = stdout.strip().lower() == "true"
    else:
        elevated = os.geteuid() == 0

    level = "root/admin" if elevated else "standard user"
    print(f"{Colors.YELLOW}[*] Current privilege level: {level}{Colors.END}")
    report.add(
        Finding(
            cve="LOCAL-CONTEXT",
            category="local",
            confidence="INFO",
            notes=f"Assessment running as {level}",
        )
    )


def run_local_checks(report: ScanReport) -> None:
    check_local_privileges(report)
    check_linux_kernel_surface(report)
    check_azure_arc_windows(report)
    check_windows_cloud_filter(report)
    check_bitlocker_winre(report)
    check_windows_service_hijack_surface(report)
