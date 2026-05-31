# Red Team Advanced Playbook

**Cutting-Edge Custom Exploitation Framework — ALL_SEEING_EYE**

> Authorized security testing only. This repo ships **recon and fingerprinting** tooling plus **TTP documentation** for purple team detection. Weaponized exploit payloads, C2 implants, persistence frameworks, and evasion/injection code are documented for detection mapping — use licensed frameworks (Cobalt Strike, Sliver, Metasploit) for authorized post-exploit work.

```bash
python3 ase.py playbook advanced
python3 tools/aura.py --target example.com
python3 ase.py scan target.com --aggressive --shodan
```

---

## Table of Contents

1. [Reconnaissance Framework (AURA)](#1-reconnaissance-framework-aura)
2. [CVE Targeting & Fingerprinting](#2-cve-targeting--fingerprinting)
3. [Post-Exploitation TTPs (PHANTOM class)](#3-post-exploitation-ttps-phantom-class)
4. [Persistence TTPs (SHADOW class)](#4-persistence-ttps-shadow-class)
5. [Evasion TTPs (GHOST class)](#5-evasion-ttps-ghost-class)
6. [Troubleshooting Guide](#6-troubleshooting-guide)

**Detection cross-reference:** [docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md](ttps/POST_EXPLOIT_TTP_REFERENCE.md)

---

## 1. Reconnaissance Framework (AURA)

**AURA** — Automated Unified Reconnaissance Assistant — lives at `tools/aura.py`.

Combines subdomain enumeration, port discovery (nmap or fallback), CVE fingerprinting via ALL_SEEING_EYE checks, and legacy banner hints.

### Usage

```bash
# Full recon pipeline
python3 tools/aura.py --target example.com

# Faster — skip subdomain brute
python3 tools/aura.py --target example.com --skip-subdomains

# Custom wordlist and ports
python3 tools/aura.py --target example.com \
  --wordlist data/wordlists/subdomains.txt \
  --ports 1-65535 \
  --workers 30 \
  --output-dir reports/aura

# Via unified CLI
python3 ase.py aura example.com
```

### Pipeline phases

| Phase | Function | Output |
|-------|----------|--------|
| Subdomain enum | DNS brute against `data/wordlists/subdomains.txt` | `subdomains[]` |
| Port scan | nmap `-p` (or socket fallback) | `open_ports[]` per host |
| CVE fingerprint | `lib/remote_checks.py` full extended set | `findings[]` |
| Legacy banners | nmap `-sV` Apache/OpenSSH hints | `legacy_cve_hints[]` |

### Integration with Shodan

```bash
# Passive first
python3 tools/shodan_recon.py domain example.com
python3 tools/shodan_recon.py hunt --net SCOPE --count-only

# Active AURA on discovered hosts
python3 tools/aura.py --target example.com
python3 ase.py scan discovered.host.example.com --shodan
```

---

## 2. CVE Targeting & Fingerprinting

Fingerprinting modules in this repo — **not weaponized exploits**.

### CVE-2023-49103 — ownCloud (graphapi disclosure)

**Detect:**

```bash
curl -sk "https://TARGET/status.php" | grep -i owncloud
python3 ase.py scan https://TARGET --aggressive
```

**Patch:** ownCloud ≥10.13.0 / 10.12.5 / 10.11.5. Remove or patch graphapi.

**Blue:** Block `/apps/graphapi/vendor/microsoft/microsoft-graph/tests/Proxy/`

---

### CVE-2023-35078 — MobileIron API bypass

**Detect:**

```bash
curl -sk "https://TARGET/mifs/.well-known/known-issues"
python3 tools/remote_scan.py TARGET
```

**Patch:** Ivanti/MobileIron security advisory. Restrict `/mifs/` to MDM-managed devices.

---

### CVE-2023-4966 — Citrix Bleed

**Detect:**

```bash
curl -sk "https://TARGET/vpn/index.html" | grep -i citrix
curl -skI "https://TARGET/oauth/idp/.well-known/openid-configuration"
```

**Patch:** Citrix ADC/Gateway fixed builds. Rotate all session tokens post-patch.

**Blue:** Alert on oversized `NSC_AAAC` cookie requests to OAuth endpoints.

---

### Full CVE catalog

```bash
python3 ase.py cves --section remote
python3 ase.py shodan dorks
```

For authorized exploitation PoC beyond fingerprinting, use Metasploit modules and vendor advisories under written ROE.

---

## 3. Post-Exploitation TTPs (PHANTOM class)

**PHANTOM** describes a C2/lateral-movement implant pattern: TCP beacon, JSON metadata, remote shell, file transfer, screenshot, persistence hooks, SMB/SSH lateral movement.

This repo does **not** ship PHANTOM source. Full behavioral mapping for defenders:

→ [docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md#phantom-c2--lateral-movement-class](ttps/POST_EXPLOIT_TTP_REFERENCE.md)

### Detection rules deployed

| Rule | Path |
|------|------|
| C2 beacon pattern | `purple/detection/sigma/c2_beacon_pattern.yml` |
| Process injection | `purple/detection/sigma/suspicious_process_injection.yml` |
| LSASS access | `purple/detection/sigma/lsass_memory_access.yml` |

### Authorized red team alternatives

| Need | Tool |
|------|------|
| C2 framework | Sliver, Cobalt Strike (licensed) |
| Lateral movement | Impacket (`smbexec.py`, `wmiexec.py`) |
| SSH pivot | `ssh -D` / Chisel (scoped) |

### Expected purple loop validation

Red runs licensed C2 in lab → Blue validates `c2_beacon_pattern.yml` fires within 5 minutes.

---

## 4. Persistence TTPs (SHADOW class)

**SHADOW** describes multi-method persistence: registry Run keys, services, cron, launchd, startup folder, WMI subscriptions, DLL hijacking.

Behavioral reference:

→ [docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md#shadow-persistence-class](ttps/POST_EXPLOIT_TTP_REFERENCE.md)

### Detection rules

| Method | Sigma / control |
|--------|-----------------|
| Registry Run | `registry_run_key_persistence.yml` |
| WMI subscription | `wmi_persistence.yml` |
| Service create | Windows Event 7045 |
| DLL hijack | Sysmon 7/11 unsigned DLL |

### Post-engagement cleanup checklist

- [ ] `autoruns.exe` / `Get-CimInstance Win32_StartupCommand`
- [ ] `wmic /namespace:\\root\subscription PATH __EventConsumer GET`
- [ ] `crontab -l` on Linux footholds
- [ ] Compare against red team IOC log in `exercise/ioc_log.json`

### Atomic Red Team validation

```bash
# Test registry persistence detection (lab only)
# T1547.001 — Atomic Red Team
```

---

## 5. Evasion TTPs (GHOST class)

**GHOST** describes sandbox/debugger detection, sleep-skipping, XOR/polymorphic shellcode, process hollowing, and remote thread injection.

This repo does **not** ship `ghost.py` or any deployable evasion/injection code. The CLI surface below is documented for **purple team detection mapping** only.

Behavioral reference:

→ [docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md#ghost-evasion-class](ttps/POST_EXPLOIT_TTP_REFERENCE.md)

### GHOST-class CLI → detection map (reference only)

| Reference command | Red behavior (lab) | What blue should see |
|-------------------|--------------------|----------------------|
| `monitor` | Continuous env polling | Repeated reads of VM/debugger artifacts |
| `check_sandbox` | VM file/registry probes | T1497 — VBox/VMware path access |
| `check_debugger` | Debugger API calls | T1622 — debug object / early exit |
| `check_analysis` | Analyst tool process enum | Unusual process enumeration |
| `encrypt_shellcode` | XOR/AES payload prep | High-entropy RX memory (EDR) |
| `polymorphic_shellcode` | Junk-byte mutation | T1027.002 — entropy / YARA |
| `process_hollowing` | Suspend → inject → resume | `process_hollowing_indicators.yml` |
| `thread_injection` | Remote thread in target PID | `suspicious_process_injection.yml`, Sysmon 8 |

### Detection rules

| Technique | Rule |
|-----------|------|
| Process hollowing | `process_hollowing_indicators.yml` |
| Thread injection | `suspicious_process_injection.yml` |
| AMSI bypass | PowerShell 4104 script block anomalies |
| Sandbox evasion | Correlate T1497 reads + subsequent injection |

### Defensive baseline

```powershell
powershell -File purple/detection/scripts/enable-windows-logging.ps1
sysmon -accepteula -i purple\detection\sysmon\sysmon-detection.xml
```

### Hunting

```powershell
powershell -File purple/detection/hunting/hunt-powershell-obfuscation.ps1
powershell -File purple/detection/hunting/hunt-suspicious-network.ps1
powershell -File purple/detection/hunting/hunt-unusual-parent-child.ps1
```

### Purple pro tips (detection validation)

1. **Fingerprint before claim** — run `ase scan --aggressive` and manual curl before asserting CVE exposure in reports.
2. **Non-standard C2 ports** — blue should monitor 8443, 5353, high ephemeral outbound (not just 4444).
3. **Obfuscation** — hunt for `pyarmor`, `Cython` artifacts and unsigned Python bundles; do not deploy obfuscated implants from this repo.
4. **Memory vs disk** — prioritize Sysmon 1/8/10 and EDR memory scans over file-only AV.
5. **Time-based evasion** — purple sandboxes should allow ≥300s dwell before verdict; correlate sleep + network.
6. **Kill chain mapping** — log each TTP in `exercise/ioc_log.json` and `exercise/detection_matrix.csv`.

---

## 6. Troubleshooting Guide

### AURA / recon issues

| Problem | Fix |
|---------|-----|
| Port scan empty / blocked | Run with appropriate scope approval; verify `which nmap`; try `ase scan` (Python sockets) or Shodan host history |
| No subdomains found | Expand `data/wordlists/subdomains.txt`; try Shodan DNS |
| nmap not found | `apt install nmap` or use `--skip-subdomains` + `ase scan` |
| All ports filtered | Target behind WAF/CDN — use Shodan; prefer `tlsx` via `ase network` over SYN scans |
| False positive CVE hits | Confirm with manual curl; check version in banner |
| Rate limited | Reduce `--workers`; add sleep between hosts |
| Corporate proxy blocks outbound | Set `http_proxy` / `https_proxy` before Shodan or curl checks |

### CVE fingerprint issues (not exploit tuning)

| Problem | Fix |
|---------|-----|
| ownCloud / graphapi inconclusive | `curl -sk https://TARGET/status.php`; confirm version ≥10.13.0; block graphapi at WAF |
| MobileIron `/mifs/` returns 401/403 | Scan 443, 8443, 9090 with `ase scan`; may be patched or allowlisted — document as hardened |
| Citrix `/vpn/` present but no advisory match | Compare build to Citrix bulletin; rotate sessions if historically vulnerable |
| Exploit PoC fails in lab | **Out of scope** — use Metasploit/vendor PoC under ROE; this repo fingerprints only |

### PHANTOM-class C2 (detection validation)

| Problem | Fix |
|---------|-----|
| Licensed C2 beacons, no SIEM alert | Import `c2_beacon_pattern.yml`; confirm NetFlow/EDR retention ≥24h |
| Large payload sessions dropped | Blue: check MTU/VPN fragmentation logs — not an implant config guide |
| JSON/metadata beacons missed | Hunt long-lived `python.exe` / unusual interpreters with periodic outbound TCP |

### SHADOW-class persistence (cleanup & detection)

| Problem | Fix |
|---------|-----|
| Persistence rule missed on Linux server | Hunt `systemd` units, `/etc/cron*`, `@reboot` — headless hosts skip desktop autostart |
| WMI subscription not logged | Enable Sysmon 19–21; deploy `wmi_persistence.yml` |
| Post-exercise artifacts remain | Red: document all methods in `exercise/ioc_log.json`; Blue: verify removal per checklist in §4 |

### GHOST-class evasion (detection tuning)

| Problem | Fix |
|---------|-----|
| VM detection rule false positive | Physical host with VMware/Hyper-V installed — tune T1497 correlation; require hollow/inject sibling alert |
| Injection rule missed | Confirm Sysmon 8/10; run `hunt-unusual-parent-child.ps1` in lab |
| Sandbox-only verdict | Extend purple dwell time; GHOST-class sleep evasion defeats <120s sandboxes |

### Shodan integration

| Problem | Fix |
|---------|-----|
| `SHODAN_API_KEY not set` | Export key from https://account.shodan.io |
| Query credits exhausted | Use `hunt --count-only` first |
| Empty hunt results | Broaden query; check scope filter |

### Detection validation (purple)

| Problem | Fix |
|---------|-----|
| Red ran scan, no alert | Import `cve_recon_web_probe.yml`; tune WAF logs |
| Beacon rule noisy | Exclude known monitoring IPs |
| Persistence rule missed | Enable Sysmon registry + WMI channels |

### Reporting & exercise hygiene

All **recon** tools write JSON to `reports/` (not `~/.redteam/logs/` — that path is reference-only for third-party implants):

```bash
ls reports/aura/
ls reports/recon_*
ls reports/network/
python3 ase.py scripts   # verify which tool produced which artifact
```

Post-engagement: archive `exercise/ioc_log.json` and confirm persistence cleanup before leaving scope.

---

## Script quick reference

| Tool | Path | Command | Detection risk |
|------|------|---------|----------------|
| AURA | `tools/aura.py` | `python3 ase.py aura example.com` | Low |
| Autorecon | `tools/autorecon.py` | `python3 ase.py scan TARGET --shodan` | Low–Medium |
| Network 2026 | `tools/network_recon.py` | `python3 ase.py network TARGET` | Low |
| Mass scan | `scripts/mass_scan.sh` | `python3 ase.py mass targets.txt` | Medium |
| Shodan | `tools/shodan_recon.py` | `python3 ase.py shodan host TARGET` | Low (passive) |
| Local | `tools/local_detect.py` | `python3 ase.py local` | N/A (host-only) |

**Reference classes (not shipped — detection only):**

| Class | MITRE | Sigma / hunt |
|-------|-------|--------------|
| PHANTOM-class C2 | T1071 | `c2_beacon_pattern.yml` |
| SHADOW-class persistence | T1547 | `registry_run_key_persistence.yml`, `wmi_persistence.yml` |
| GHOST-class evasion | T1055, T1027 | `process_hollowing_indicators.yml`, `suspicious_process_injection.yml` |

Full index: `purple/script_reference.json` or `python3 ase.py scripts`

### Dependencies (this repo only)

```bash
pip install -r requirements.txt
bash scripts/install-recon-tools.sh   # optional: tlsx, nuclei, katana
```

Third-party implant deps (`pyautogui`, `paramiko`, `pywin32`, `lief`, etc.) apply to **licensed C2/lab tooling outside this repo** — not included in `requirements.txt`.

---

## Related documents

| Doc | Command |
|-----|---------|
| Red engagement playbook | `python3 ase.py playbook red` |
| Blue defensive playbook | `python3 ase.py playbook blue` |
| Purple exercise playbook | `python3 ase.py playbook purple` |
| Purple detection handbook | `python3 ase.py handbook purple` |
| TTP detection reference | `docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md` |
