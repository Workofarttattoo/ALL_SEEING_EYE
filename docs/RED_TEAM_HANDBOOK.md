# Red Team Handbook 2025–2026

**ALL_SEEING_EYE — Authorized Reconnaissance & CVE Fingerprinting**

> Use only on systems you own or have explicit written authorization to test.
> This toolkit performs **detection and fingerprinting only** — not exploitation, persistence, exfiltration, or anti-forensics.

---

## Section 1: Current High-Value Targets (Active Exploitation)

| CVE | Target | CVSS | Status | Notes |
|-----|--------|------|--------|-------|
| CVE-2025-31324 | SAP NetWeaver Visual Composer | 10.0 | ACTIVE | Unauthenticated file upload → RCE |
| CVE-2025-42999 | SAP NetWeaver | 9.9 | ACTIVE | Related to 31324 |
| CVE-2025-32433 | Erlang SSH Library | 9.8 | ACTIVE | SSH-based, no creds needed |
| CVE-2025-55182 | React / Next.js | 9.8 | ACTIVE | React2Shell SSRF→RCE chain |
| CVE-2025-66478 | Next.js | 9.8 | ACTIVE | Server-side exploitation |
| CVE-2025-53521 | F5 BIG-IP | 9.8 | ACTIVE | iControl REST RCE |
| CVE-2026-29014 | MetInfo CMS 7.9–8.1 | 9.8 | ACTIVE | PHP code injection |
| CVE-2026-20223 | Cisco REST API | 10.0 | CRITICAL | Auth bypass |
| CVE-2025-14847 | MongoDB (MongoBleed) | 8.2 | ACTIVE | Memory leak → info disclosure |
| CVE-2025-0520 | ShowDoc <2.8.7 | 9.8 | ACTIVE | 2000+ instances exposed |
| CVE-2026-34621 | Adobe Acrobat | 9.8 | ACTIVE | Active exploitation (user interaction) |
| CVE-2025-59528 | Flowise AI | 9.1 | ACTIVE | AI framework targeting |

---

## Section 2: Exploit Matrix (Remote vs Local)

### Remote (network-deployable)

| CVE | Target | CVSS | Auth |
|-----|--------|------|------|
| CVE-2026-21992 | Oracle Identity Manager | 9.8 | None |
| CVE-2026-27577 | n8n Workflow | 9.4 | Auth |
| CVE-2026-27493 | n8n Workflow | 9.5 | None |
| CVE-2026-21858 | n8n Workflow | 9.8 | Auth |
| CVE-2026-45498 | Microsoft Defender | 8.8 | None |
| CISCO-ISE-RCE | Cisco Identity Services | 9.8 | None |
| CISCO-FMC-RCE | Cisco Firewall Management | 9.8 | None |

### Local / physical (touch required)

| CVE | Target | CVSS | Access |
|-----|--------|------|--------|
| CVE-2026-31431 | Linux Kernel (Copy Fail) | 7.8 | Local user |
| CVE-2026-43500 | Linux Kernel (Dirty Frag) | 7.8 | Local user |
| CVE-2026-26117 | Azure Arc Windows | 7.8 | Local user |
| CVE-2025-62221 | Windows Cloud Filter | 7.8 | Local user |
| CVE-2025-54100 | Windows Multiple | 8.8 | Local user |
| YELLOWKEY | Windows BitLocker | N/A | Physical USB |

---

## Section 3: Toolkit Commands

### Unified CLI (`ase.py`)

```bash
# Install dependencies
pip install -r requirements.txt

# Single-target full recon
python3 ase.py scan https://target.example

# Extended remote checks (Oracle, n8n, Cisco)
python3 ase.py scan target.example --aggressive

# Remote-only fingerprint
python3 ase.py remote https://target.example

# Local system indicator scan
python3 ase.py local

# Bulk scan from file
python3 ase.py mass targets.txt

# Rapid extended remote identification
python3 ase.py rapid high_value_targets.txt

# List tracked CVEs
python3 ase.py cves --section remote

# Print this handbook
python3 ase.py handbook
```

### Direct tool invocation

```bash
python3 tools/autorecon.py https://target.example --aggressive
python3 tools/remote_scan.py target.example
python3 tools/local_detect.py
bash scripts/mass_scan.sh targets.txt
bash scripts/rapid_scan.sh targets.txt
```

---

## Section 4: Detection One-Liners

Use these for manual validation during authorized assessments.

### SAP NetWeaver (CVE-2025-31324)

```bash
curl -sk "https://TARGET/VisualComposer/VCFramework.wdvc" | grep -i sap
```

### F5 BIG-IP (CVE-2025-53521)

```bash
curl -sk "https://TARGET/tmui/login.jsp" | grep -i "f5\|big-ip"
```

### React/Next.js (CVE-2025-55182 / 66478)

```bash
curl -skI "https://TARGET/" | grep -i next
curl -sk "https://TARGET/_next/static/" -o /dev/null -w "%{http_code}\n"
```

### MetInfo CMS (CVE-2026-29014)

```bash
curl -sk "http://TARGET/" | grep -i metinfo
```

### ShowDoc (CVE-2025-0520)

```bash
curl -sk "http://TARGET/server/index.php" | grep -i showdoc
```

### MongoDB (CVE-2025-14847)

```bash
nc -zv TARGET 27017
# or: mongosh "mongodb://TARGET:27017" --eval "db.version()"
```

### n8n (CVE-2026-27493 / 21858)

```bash
curl -sk "http://TARGET/healthz" | grep -i n8n
```

### Oracle Identity Manager (CVE-2026-21992)

```bash
curl -sk "https://TARGET/oim/faces/adf.task-flow" | grep -i oracle
```

---

## Section 5: Shodan Integration (Passive Intel)

Shodan aggregates **public banners** from Internet-wide scanning and parses them into searchable fields (`product`, `port`, `http.*`, `vuln`, `org`, etc.). ALL_SEEING_EYE maps your CVE catalog to Shodan filter syntax in `data/shodan_dorks.json`.

```bash
export SHODAN_API_KEY="your_key"   # https://account.shodan.io

# View CVE → Shodan dork mappings (no API key needed)
python3 ase.py shodan dorks

# Count global exposure cheaply before searching
python3 tools/shodan_recon.py hunt --cve CVE-2025-53521 --count-only

# Scope to engagement target
python3 tools/shodan_recon.py hunt --org "Target Corp" --count-only
python3 tools/shodan_recon.py hunt --net 10.0.0.0/8 --cve CVE-2025-14847

# Subdomain seeding + host profile
python3 ase.py shodan domain target.com
python3 ase.py shodan host 203.0.113.10

# Merge Shodan banners/vulns into active scan
python3 ase.py scan target.com --shodan --aggressive
```

Full guide: [docs/SHODAN.md](SHODAN.md)

Team playbooks: `python3 ase.py playbook blue|red|purple`

---

## Section 6: Automated Workflow

```bash
# 0. Shodan-first (passive) — scope with org/net/hostname filters
python3 tools/shodan_recon.py hunt --count-only
python3 tools/shodan_recon.py domain target.com -o reports/dns.json

# 1. Discovery — parallel autorecon with Shodan enrichment
cat targets.txt | xargs -P10 -I{} python3 tools/autorecon.py {} --aggressive --shodan

# 2. Mass fingerprint
bash scripts/mass_scan.sh targets.txt

# 3. Extended remote identification
bash scripts/rapid_scan.sh high_value_targets.txt

# 4. Local assessment on lab host
python3 tools/local_detect.py

# 5. Review JSON reports
ls -la reports/
```

---

## Section 7: OPSEC Notes (Authorized Testing)

- Obtain written scope and rules of engagement before scanning
- Use rate limiting and jitter between requests (1–5 seconds)
- Rotate User-Agent strings when permitted by ROE
- Log all activity to your engagement tracker
- Stop immediately if you exceed scope
- Report findings through your team's standard channel

---

## Section 8: What This Toolkit Does NOT Include

The following are intentionally out of scope for this repository:

- Weaponized exploit payloads or webshell upload
- C2 listeners, RATs, or persistence mechanisms
- Data exfiltration utilities
- Anti-forensics or registry tampering
- Unauthorized user session manipulation

For authorized post-exploitation in professional engagements, use licensed commercial frameworks (Cobalt Strike, Sliver, etc.) under proper contract and legal authorization.

---

## Section 9: Report Format

JSON reports are written to `reports/` (or `scan_results_*/json/` during mass scans):

```json
{
  "target": "example.com",
  "timestamp": "2026-05-31T12:00:00+00:00",
  "open_ports": [80, 443],
  "findings": [
    {
      "cve": "CVE-2025-66478",
      "confidence": "MEDIUM",
      "notes": "Next.js framework detected",
      "category": "remote"
    }
  ]
}
```

---

## Section 10: Project Layout

```
ALL_SEEING_EYE/
├── ase.py                 # Main CLI entry point
├── data/cves.json         # CVE catalog
├── data/shodan_dorks.json # CVE → Shodan filter mappings
├── docs/RED_TEAM_HANDBOOK.md
├── docs/SHODAN.md         # Shodan integration guide
├── lib/                   # Shared detection + Shodan modules
├── tools/                 # autorecon, shodan_recon, local_detect, remote_scan
├── scripts/               # mass_scan.sh, rapid_scan.sh
└── reports/               # Generated scan output (gitignored)
```
