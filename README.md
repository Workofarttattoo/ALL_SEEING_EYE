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

## Project Structure

```
├── ase.py              # Unified CLI
├── data/cves.json      # CVE catalog (remote + local)
├── docs/               # Red team handbook
├── lib/                # Detection modules
├── tools/              # autorecon, local_detect, remote_scan
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
