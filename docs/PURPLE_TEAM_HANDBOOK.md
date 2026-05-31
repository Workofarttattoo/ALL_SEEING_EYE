# Purple Team Handbook

**Defensive Detection & Response Guide — ALL_SEEING_EYE**

> Detection, defense, and response for authorized purple team exercises. Pairs with [PURPLE_TEAM_PLAYBOOK.md](PURPLE_TEAM_PLAYBOOK.md) (exercise cadence) and the toolkit script reference in [../purple/script_reference.json](../purple/script_reference.json).

```bash
python3 ase.py handbook purple          # print this handbook
python3 ase.py scripts                  # list all toolkit + detection scripts
python3 ase.py scripts --phase reconnaissance
```

---

## Section 0: Toolkit & Script Reference (Single Location)

All ALL_SEEING_EYE scripts, detection rules, and hunting queries in one index.

### 0.1 Recon & fingerprint scripts (red / purple red side)

| Script | Path | Command | Attack phase | Blue detects via |
|--------|------|---------|--------------|------------------|
| **ase** | `ase.py` | `python3 ase.py scan <target> --aggressive --shodan` | Recon, Discovery | Child process spawn chain |
| **autorecon** | `tools/autorecon.py` | `python3 tools/autorecon.py <target> [--aggressive] [--shodan]` | Recon, Discovery | Port scan + CVE paths (Sigma 004) |
| **remote_scan** | `tools/remote_scan.py` | `python3 tools/remote_scan.py <target>` | Recon | Web probe rules |
| **mass_scan** | `scripts/mass_scan.sh` | `bash scripts/mass_scan.sh targets.txt` | Recon | Multi-path curl pattern |
| **rapid_scan** | `scripts/rapid_scan.sh` | `bash scripts/rapid_scan.sh targets.txt` | Recon | Oracle/Cisco/n8n paths |
| **shodan_recon** | `tools/shodan_recon.py` | `python3 tools/shodan_recon.py hunt\|host\|domain` | Recon (passive) | Shodan footprint audit |
| **local_detect** | `tools/local_detect.py` | `python3 ase.py local` | Discovery, Priv esc | EDR + PowerShell recon |

### 0.2 Detection rules & hunting (blue / purple blue side)

| Asset | Path | Type | MITRE | Deploy |
|-------|------|------|-------|--------|
| Registry Run Key Persistence | `purple/detection/sigma/registry_run_key_persistence.yml` | Sigma | T1547.001 | SIEM import |
| Process Injection | `purple/detection/sigma/suspicious_process_injection.yml` | Sigma | T1055 | SIEM import |
| LSASS Memory Access | `purple/detection/sigma/lsass_memory_access.yml` | Sigma | T1003.001 | SIEM import |
| CVE Web Probe (ASE) | `purple/detection/sigma/cve_recon_web_probe.yml` | Sigma | T1595 | WAF + SIEM |
| PowerShell obfuscation hunt | `purple/detection/hunting/hunt-powershell-obfuscation.ps1` | Hunt | T1059.001 | Manual / SOAR |
| Suspicious network hunt | `purple/detection/hunting/hunt-suspicious-network.ps1` | Hunt | C2 | Manual |
| Parent-child process hunt | `purple/detection/hunting/hunt-unusual-parent-child.ps1` | Hunt | T1059 | Manual |
| Sysmon detection config | `purple/detection/sysmon/sysmon-detection.xml` | Sysmon | All | Endpoint deploy |
| Windows logging baseline | `purple/detection/scripts/enable-windows-logging.ps1` | Config | Prep | GPO / Intune |

### 0.3 Script → purple loop mapping

| Loop | Red runs | Blue deploys | Scorecard row |
|------|----------|--------------|---------------|
| 1 | `shodan_recon.py hunt --count-only` | CMDB vs Shodan | `exercise/detection_matrix.csv` loop 1 |
| 2 | `mass_scan.sh scope.txt` | Sigma 004 + port scan | loop 2 |
| 3 | `autorecon.py --shodan` | Log correlation | loop 3 |
| 4 | Manual SSRF probe | WAF + IMDS block | loop 4 |
| 5 | Port 27017 check | Firewall deny | loop 5 |
| 6 | curl `/healthz` `/form` | AppSec alert | loop 6 |
| 7 | `local_detect.py` on lab VM | EDR | loop 7 |
| 8 | Full `ase.py scan` chain | IR + contain | loop 8 |

Machine-readable index: `purple/script_reference.json`

---

## Section 1: Attack Lifecycle Detection Matrix

| Attack Phase | Red Team Activity | Blue Team Detection | Response Action |
|--------------|-------------------|---------------------|-----------------|
| Reconnaissance | Port scanning, OSINT, `autorecon`, Shodan, `mass_scan.sh` | SIEM scan patterns; Shodan org monitoring; Sigma CVE probe | Block IOCs; increase logging |
| Initial Access | Phishing, exploited vulnerability | Email gateway; IDS; EDR behavioral alerts | Isolate endpoint; revoke tokens |
| Execution | Malware, scripts, PowerShell | Process creation; PS logging; AMSI | Kill process; quarantine file |
| Persistence | Registry run keys, tasks, services | Registry monitoring; Sysmon; task logs | Remove persistence; clean registry |
| Privilege Escalation | Token abuse, exploits, `local_detect` LPE paths | UAC alerts; kernel/EDR callbacks | Revoke elevated sessions |
| Defense Evasion | Injection, obfuscation | AMSI/ETW tampering; anomalous API | Protected event logging |
| Credential Access | LSASS dump, Kerberoasting | LSASS access (Sigma 003); Kerberos anomalies | Force resets; revoke tickets |
| Discovery | Network scan, LDAP enum | Unusual LDAP; sweeps from one host | Restrict lateral movement |
| Lateral Movement | PSExec, WMI, RDP | SMB/RDP from new sources; WMI spawn | Disable accounts; segment |
| Collection | File access, screenshots | File patterns; screen capture APIs | DLP; classification |
| Exfiltration | Upload, DNS tunneling | Large egress; beaconing; DNS anomalies | Block egress; sinkhole |

---

## Section 2: Detection Rules (Sigma/YARA)

Rules live in `purple/detection/sigma/`. Import into SIEM or convert with [Sigma CLI](https://github.com/SigmaHQ/sigma).

### Detecting Persistence — Registry Run Keys

**File:** `purple/detection/sigma/registry_run_key_persistence.yml`

```yaml
title: Registry Run Key Persistence
status: stable
description: Detects suspicious registry modifications for persistence
logsource:
    category: registry_event
    product: windows
detection:
    selection:
        EventType: SetValue
        TargetObject|contains:
            - '\Software\Microsoft\Windows\CurrentVersion\Run'
            - '\Software\Microsoft\Windows\CurrentVersion\RunOnce'
            - '\Software\Microsoft\Windows\CurrentVersion\RunOnceEx'
    filter_legitimate:
        Image|contains:
            - 'C:\Windows\'
            - 'C:\Program Files\'
    condition: selection and not filter_legitimate
level: medium
```

### Detecting Process Injection

**File:** `purple/detection/sigma/suspicious_process_injection.yml`

```yaml
title: Suspicious Process Access for Injection
logsource:
    category: process_access
    product: windows
detection:
    selection:
        GrantedAccess:
            - '0x1010'
            - '0x1F0FFF'
        CallTrace|contains:
            - 'kernel32.dll!OpenProcess'
            - 'kernel32.dll!VirtualAllocEx'
            - 'kernel32.dll!WriteProcessMemory'
    condition: selection
level: high
```

### Detecting LSASS Access (Credential Dumping)

**File:** `purple/detection/sigma/lsass_memory_access.yml`

```yaml
title: LSASS Memory Access
logsource:
    category: process_access
    product: windows
detection:
    target_process:
        TargetImage|endswith: '\lsass.exe'
    granted_access:
        GrantedAccess|contains:
            - '0x1010'
            - '0x1410'
            - '0x143a'
            - '0x1430'
            - '0x100000'
    filter_legitimate:
        SourceImage|endswith:
            - '\svchost.exe'
            - '\taskmgr.exe'
            - '\services.exe'
    condition: target_process and granted_access and not filter_legitimate
level: critical
```

### Detecting ALL_SEEING_EYE CVE Recon

**File:** `purple/detection/sigma/cve_recon_web_probe.yml`

Detects `autorecon.py` and `mass_scan.sh` fingerprint patterns against SAP, F5, n8n, Next.js, ShowDoc, Oracle OIM, Flowise paths.

---

## Section 3: Hunting Queries

Scripts in `purple/detection/hunting/`. Run on domain-joined endpoints during purple loops or daily hunts.

### PowerShell Obfuscation Detection

**File:** `purple/detection/hunting/hunt-powershell-obfuscation.ps1`

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Microsoft-Windows-PowerShell/Operational'
    ID=4104
} | Where-Object {
    $_.Message -match 'encodedcommand|enc\s|FromBase64String|bxor|::Compress|Invoke-Expression|IEX'
}
```

### Suspicious Network Connections

**File:** `purple/detection/hunting/hunt-suspicious-network.ps1`

```powershell
Get-NetTCPConnection | Where-Object {
    $_.RemoteAddress -notmatch '^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|127\.)' -and
    $_.RemotePort -notin @(80,443,53,123) -and
    $_.State -eq 'Established'
} | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess
```

### Unusual Parent-Child Process Relationships

**File:** `purple/detection/hunting/hunt-unusual-parent-child.ps1`

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    ID=4688
} | Where-Object {
    $_.Message -match 'winword\.exe.*cmd\.exe' -or
    $_.Message -match 'excel\.exe.*powershell\.exe' -or
    $_.Message -match 'outlook\.exe.*wscript\.exe'
}
```

---

## Section 4: Incident Response Playbooks

### Playbook: Malware Detection on Endpoint

**Detection:** EDR alert for suspicious process execution

**Immediate (0–10 min):**

1. Isolate endpoint (preserve evidence)
2. Capture volatile memory (WinPMEM, Magnet RAM Capture)
3. Snapshot processes and network connections
4. Identify logged-in user

**Analysis (10–60 min):**

- Collect: Prefetch, Recent files, browser history, temp dirs, registry hives
- Analyze: Sandbox (Any.Run, Joe Sandbox), static PE analysis, VirusTotal/OTX

**Containment (1–4 h):**

- Block hashes, IPs, domains
- Disable compromised accounts
- Hunt lateral movement in auth logs and netflow

**Eradication (4–24 h):**

- Reimage (don't clean-in-place)
- Reset passwords; reissue certs if needed
- Remove persistence fleet-wide

**Recovery (24–72 h):**

- Restore from known-good backups
- Validate no persistence
- Enhanced monitoring on affected accounts

**Post-incident:**

- Timeline reconstruction
- Root cause analysis
- Detection gap analysis → update `purple/detection/sigma/`
- Log in `exercise/detection_matrix.csv`

---

## Section 5: Purple Team Exercise Scenarios

Full loop schedule: [PURPLE_TEAM_PLAYBOOK.md](PURPLE_TEAM_PLAYBOOK.md)

### Scenario 1: Phishing with Malicious Attachment

| | |
|---|---|
| **Red objective** | Initial access via Office macro |
| **Blue objective** | Block/detect before execution |
| **Chain** | Phish → macro doc → payload → persistence → recon |
| **Detection** | Email gateway; AMSI; Office→cmd spawn; payload download |
| **Metrics** | Red: execution undetected / Blue: block at gateway or pre-exec |

### Scenario 2: Lateral Movement via WMI

| | |
|---|---|
| **Red objective** | Workstation → server |
| **Blue objective** | Detect lateral movement |
| **Chain** | Compromise WS → cred harvest → WMI exec → server backdoor |
| **Detection** | Admin logins; WMI :135; PowerShell via WMI; new service |
| **Toolkit tie-in** | After foothold: `python3 ase.py local` for LPE indicators |

### Scenario 3: Data Exfiltration via DNS Tunneling

| | |
|---|---|
| **Red objective** | Exfil without DLP trigger |
| **Blue objective** | Detect anomalous DNS |
| **Chain** | Compress → encode in DNS → attacker DNS reassembly |
| **Detection** | High query volume; long queries; new domains; process DNS spam |

### Scenario 4: ALL_SEEING_EYE CVE Recon (toolkit-native)

| | |
|---|---|
| **Red objective** | Map CVE exposure in scope |
| **Blue objective** | Alert ≤5 min on mass fingerprint |
| **Red runs** | `bash scripts/mass_scan.sh exercise/scope.txt` then `ase scan --shodan` |
| **Blue deploys** | `purple/detection/sigma/cve_recon_web_probe.yml` |
| **Purple scores** | MTTD, log completeness vs `reports/*.json` |

---

## Section 6: Defensive Tools & Configurations

### Sysmon Configuration

**File:** `purple/detection/sysmon/sysmon-detection.xml`

Deploy:

```powershell
sysmon -accepteula -i purple\detection\sysmon\sysmon-detection.xml
```

Covers: process creation, network from LOLBins, LSASS access, Run key registry, download folder file creation.

### Windows Event Logging Baseline

**File:** `purple/detection/scripts/enable-windows-logging.ps1`

```powershell
powershell -ExecutionPolicy Bypass -File purple/detection/scripts/enable-windows-logging.ps1
```

Enables: PowerShell script block logging, transcription, process creation 4688, command line in audit.

---

## Section 7: MITRE ATT&CK Mapping

| Technique | Detection Strategy | Data Sources | ASE Script / Rule |
|-----------|-------------------|--------------|-------------------|
| T1595 — Active Scanning | CVE path + port scan rules | WAF, firewall, SIEM | `autorecon`, `mass_scan`, Sigma 004 |
| T1590 — Gather Victim Network Info | Shodan footprint audit | Shodan, CMDB | `shodan_recon.py` |
| T1566.001 — Spearphishing Attachment | Email + macro AMSI | Email gateway, EDR | Scenario 1 |
| T1059.001 — PowerShell | Script block logging | Event 4104 | `hunt-powershell-obfuscation.ps1` |
| T1055 — Process Injection | Process access | Sysmon, EDR | Sigma 002 |
| T1547.001 — Registry Run Keys | Registry events | Sysmon | Sigma 001 |
| T1003.001 — LSASS Memory | LSASS access | Sysmon | Sigma 003 |
| T1021.002 — SMB/Admin Shares | Network monitoring | Firewall, Netflow | Scenario 2 |
| T1041 — Exfil Over C2 | Beaconing | IDS, proxy | — |
| T1071.004 — DNS Exfil | DNS analytics | DNS logs | Scenario 3 |
| T1068 — Exploitation for Priv Esc | EDR + kernel patch | EDR, `ase local` | `local_detect.py` |

---

## Section 8: Directory Layout

```
purple/
├── script_reference.json       # Machine-readable script + detection index
├── detection/
│   ├── sigma/                  # 4 Sigma rules (import to SIEM)
│   ├── hunting/                # 3 PowerShell hunt scripts
│   ├── sysmon/                 # Sysmon XML config
│   └── scripts/                # Windows logging baseline
docs/
├── PURPLE_TEAM_HANDBOOK.md     # This document — detection & response
└── PURPLE_TEAM_PLAYBOOK.md     # Exercise loops & flip protocol
exercise/
├── scope.txt
├── ioc_log.json
└── detection_matrix.csv
```

---

## Section 9: Quick Commands

```bash
# Handbook & scripts
python3 ase.py handbook purple
python3 ase.py scripts
python3 ase.py scripts --detection

# Red side (authorized scope only)
python3 ase.py scan target.com --aggressive --shodan
bash scripts/mass_scan.sh exercise/scope.txt

# Blue side — deploy detection
# Import purple/detection/sigma/*.yml to SIEM
powershell -File purple/detection/hunting/hunt-powershell-obfuscation.ps1

# Purple scoring
# Edit exercise/detection_matrix.csv after each loop
```

---

## Related Documents

| Document | Command |
|----------|---------|
| Purple exercise playbook | `python3 ase.py playbook purple` |
| Blue defensive playbook | `python3 ase.py playbook blue` |
| Red engagement playbook | `python3 ase.py playbook red` |
| Red CVE handbook | `python3 ase.py handbook` |
| Shodan integration | `docs/SHODAN.md` |
