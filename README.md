# ALL_SEEING_EYE

Autonomous CVE-focused reconnaissance framework for **authorized** red team and security assessment work.

Detection and fingerprinting only — identifies exposed services, framework indicators, and patch-review targets across the 2025–2026 active CVE landscape. Split coverage between **remote** (network-reachable) and **local/physical** (requires shell or physical access).

## Quick Start

```bash
pip install -r requirements.txt

# Scan a single target
python3 ase.py scan https://target.example

# Extended remote checks (Oracle IEM, n8n, Cisco)
python3 ase.py scan target.example --aggressive

# Local system indicators
python3 ase.py local

# Bulk scan
python3 ase.py mass targets.txt

# View handbook
python3 ase.py handbook
```

## Commands

| Command | Description |
|---------|-------------|
| `ase scan <target>` | Full autorecon with port scan + CVE checks |
| `ase remote <target>` | Remote fingerprint only |
| `ase local` | Local/physical CVE indicators on current host |
| `ase mass <file>` | Bulk scan via `scripts/mass_scan.sh` |
| `ase rapid <file>` | Extended remote ID via `scripts/rapid_scan.sh` |
| `ase cves [--section remote\|local\|all]` | List tracked CVEs |
| `ase handbook` | Print red team handbook |
| `ase playbook blue` | Blue team defensive playbook |
| `ase playbook red` | Red team engagement playbook |
| `ase playbook purple` | Purple team collaborative playbook |
| `ase shodan dorks` | List CVE → Shodan query mappings |
| `ase shodan host <ip>` | Shodan host profile |
| `ase shodan domain <domain>` | Subdomain/DNS intel |
| `ase shodan hunt` | Hunt CVE dorks against Shodan index |
| `ase scan <target> --shodan` | Active scan + Shodan enrichment |

## Shodan Integration

Shodan indexes public Internet banners into searchable fields. ALL_SEEING_EYE maps your CVE catalog to Shodan filter syntax and enriches scans with historical host data.

```bash
export SHODAN_API_KEY="your_key"   # https://account.shodan.io

python3 ase.py shodan dorks                              # no key needed
python3 ase.py shodan host target.com
python3 ase.py shodan domain target.com
python3 tools/shodan_recon.py hunt --count-only          # scout cheaply
python3 ase.py scan target.com --shodan --aggressive
```

See [docs/SHODAN.md](docs/SHODAN.md) for the full data model, credit tips, and workflow.

## Project Structure

```
├── ase.py              # Unified CLI
├── data/cves.json      # CVE catalog (remote + local)
├── data/shodan_dorks.json  # CVE → Shodan filter mappings
├── docs/               # Handbooks and playbooks (blue/red/purple)
├── purple/detection/   # Sigma rules, hunting scripts, Sysmon config
├── lib/                # Detection modules
├── tools/              # autorecon, local_detect, remote_scan, shodan_recon
├── scripts/            # Bash bulk scanners
└── reports/            # JSON output (generated)
```

## Authorization

**Only use against systems you own or have explicit written permission to test.** Unauthorized scanning may violate computer fraud laws.

## Scope

This toolkit provides:

- CVE fingerprinting and service detection
- Port scanning (common ports)
- JSON reporting
- Bulk scanning workflows

It does **not** include exploit payloads, C2, persistence, exfiltration, or anti-forensics tooling.

See [docs/RED_TEAM_HANDBOOK.md](docs/RED_TEAM_HANDBOOK.md) for the full handbook, CVE matrix, and one-liners.

## Team Playbooks

| Playbook | Command | Role |
|----------|---------|------|
| Blue Team | `python3 ase.py playbook blue` | Defend against expected red team TTPs |
| Red Team | `python3 ase.py playbook red` | Run authorized engagement when you flip sides |
| Red Advanced | `python3 ase.py playbook advanced` | AURA recon + CVE TTP reference |
| AURA recon | `python3 ase.py aura example.com` | Subdomain + port + CVE pipeline |
| Purple Team | `python3 ase.py playbook purple` | Joint attack/defense loops and scoring |
| Purple Handbook | `python3 ase.py handbook purple` | Detection rules, hunting, IR, script index |
| Script index | `python3 ase.py scripts` | All toolkit + detection assets in one list |
| Network 2026 guide | `python3 ase.py handbook network` | QUIC/DoH/modern recon methodology |
| Network recon | `python3 ase.py network target.com` | tlsx + nuclei + ASE orchestrator |

## Education (defensive)

| Topic | Path |
|-------|------|
| PoisonTap / Venice chat archive | `Education/poisonTap/README.md` |
| Excluded weaponized content policy | `docs/EXCLUDED_CONTENT.md` |
