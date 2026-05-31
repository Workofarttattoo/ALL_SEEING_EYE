# Venice Chat — Topic Index

Archive of topics discussed in the **Venice Uncensored AI** red-team / PoisonTap conversation. This index helps you find what was **documented defensively** vs **excluded as weaponized**.

---

## Session 1 — Red team playbook (GLM / Venice)

| Section | Topic | Repo status |
|---------|-------|-------------|
| 1 | AURA recon framework | ✅ Implemented — `tools/aura.py` |
| 2 | OCLeak (CVE-2023-49103) | 🔍 Fingerprint only — `ase scan` |
| 2 | MIRCE (CVE-2023-35078) | 🔍 Fingerprint only |
| 2 | CitrixBleed (CVE-2023-4966) | 🔍 Fingerprint only |
| 3 | PHANTOM C2 / lateral movement | 📋 Detection docs only |
| 4 | SHADOW persistence | 📋 Detection docs only |
| 5 | GHOST evasion / injection | 📋 Detection docs only |
| 6 | Troubleshooting (exploits + implants) | 📋 Purple troubleshooting only |
| — | Quick reference matrix | 📋 Detection-oriented matrix in advanced playbook |
| — | Pro tips (pyarmor, C2 ports, hollow) | ❌ Excluded |

---

## Session 2 — Extended chapters (Qwen)

| Proposed chapter | Topic | Repo status |
|------------------|-------|-------------|
| 7 | Cloud / K8s (CLOUDFALL) | ❌ Not implemented |
| 8 | AD / Kerberos (KERBERUN) | ❌ Not implemented |
| 9 | AI / LLM (PROMPTFALL) | ❌ Not implemented |
| 10 | Anti-forensics (SHROUD) | ❌ Not implemented |
| — | Kill-chain combination table | 📋 Partial — TTP reference |

---

## Session 3 — PoisonTap 2026 (Qwen)

| Topic | Repo status |
|-------|-------------|
| Full Python rewrite (`poisontap_core.py`, TLS proxy) | ❌ Excluded |
| `pi_startup.sh` nftables + dnsmasq | 📋 Described in ARCHITECTURE / MITIGATIONS |
| `pi_poisontap_2026.js` | ❌ Excluded |
| `backend_server_2026.js` WSS C2 | ❌ Excluded |
| `target_backdoor_2026.js` multi-transport exfil | ❌ Excluded |
| `backdoor_2026.html` persistent WS | ❌ Excluded |
| `target_injected_xhtmljs_2026.html` | ❌ Excluded |
| `populate_cdn.sh` CDN auto-fetch | ❌ Excluded |
| Original file analysis (`backend_server.js`, etc.) | ✅ ARCHITECTURE.md |
| `/js/` CDN cache explanation | ✅ JS_CDN_CACHE.md |
| Pi Zero 2 W LED / power notes | ✅ NETWORK_2026_MITIGATIONS.md |

---

## Where to read converted content

| Need | Path |
|------|------|
| PoisonTap education | `Education/poisonTap/` |
| CVE fingerprinting | `python3 ase.py scan` |
| PHANTOM/SHADOW/GHOST detection | `docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md` |
| Excluded policy | `docs/EXCLUDED_CONTENT.md` |
| Full exclusion list from Venice | `Education/poisonTap/EXCLUDED_WEAPONIZED.md` |

---

## User intent mapping

| You asked for | We provide instead |
|---------------|-------------------|
| "Leave nothing out" exploit playbook | Full **detection** playbook + official external tools under ROE |
| "Reverse engineer and improve" PoisonTap | **Architecture reverse-engineering** + **2026 mitigation analysis** |
| Store under `Education/poisonTap` | This directory |
| Runnable 2026 PoisonTap on Pi Zero 2 W | Pointer to **official repo** for isolated lab only |
