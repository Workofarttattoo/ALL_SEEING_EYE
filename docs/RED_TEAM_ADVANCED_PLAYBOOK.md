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

**GHOST** describes sandbox/debugger detection, sleep-skipping, XOR shellcode, process hollowing, and remote thread injection.

Behavioral reference:

→ [docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md#ghost-evasion-class](ttps/POST_EXPLOIT_TTP_REFERENCE.md)

### Detection rules

| Technique | Rule |
|-----------|------|
| Process hollowing | `process_hollowing_indicators.yml` |
| Thread injection | `suspicious_process_injection.yml` |
| AMSI bypass | PowerShell 4104 script block anomalies |

### Defensive baseline

```powershell
powershell -File purple/detection/scripts/enable-windows-logging.ps1
sysmon -accepteula -i purple\detection\sysmon\sysmon-detection.xml
```

### Hunting

```powershell
powershell -File purple/detection/hunting/hunt-powershell-obfuscation.ps1
powershell -File purple/detection/hunting/hunt-suspicious-network.ps1
```

---

## 6. Troubleshooting Guide

### AURA / recon issues

| Problem | Fix |
|---------|-----|
| No subdomains found | Expand `data/wordlists/subdomains.txt`; try Shodan DNS |
| nmap not found | `apt install nmap` or use `--skip-subdomains` + `ase scan` |
| All ports filtered | Target behind WAF/CDN — use Shodan host history |
| False positive CVE hits | Confirm with manual curl; check version in banner |
| Rate limited | Reduce `--workers`; add sleep between hosts |

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

### Reporting

All tools write JSON to `reports/`:

```bash
ls reports/aura/
ls reports/recon_*
python3 ase.py scripts   # verify which tool produced which artifact
```

---

## Script quick reference

| Tool | Path | Command |
|------|------|---------|
| AURA | `tools/aura.py` | `python3 ase.py aura example.com` |
| Autorecon | `tools/autorecon.py` | `python3 ase.py scan TARGET --shodan` |
| Mass scan | `scripts/mass_scan.sh` | `python3 ase.py mass targets.txt` |
| Shodan | `tools/shodan_recon.py` | `python3 ase.py shodan host TARGET` |
| Local | `tools/local_detect.py` | `python3 ase.py local` |

Full index: `purple/script_reference.json` or `python3 ase.py scripts`

---

## Related documents

| Doc | Command |
|-----|---------|
| Red engagement playbook | `python3 ase.py playbook red` |
| Blue defensive playbook | `python3 ase.py playbook blue` |
| Purple exercise playbook | `python3 ase.py playbook purple` |
| Purple detection handbook | `python3 ase.py handbook purple` |
| TTP detection reference | `docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md` |
