# Excluded Content Policy

This repo ships **authorized recon, CVE fingerprinting, and purple-team detection**. The following categories are intentionally **not** included.

---

## Weaponized tools & source (never added)

| Item | Why excluded |
|------|--------------|
| `ghost.py` (encrypt_shellcode, polymorphic_shellcode, process_hollowing, thread_injection) | Offensive evasion/injection code |
| `phantom.py` / `phantom_listener.py` | C2 implant |
| `shadow.py` + `shadow.service` templates | Persistence implant |
| `OCLeak`, `MIRCE`, `CitrixBleed` exploit runners | Weaponized CVE PoC |
| `cve_exploit_kit.py` | Exploit orchestration |
| DNS C2, memory droppers, EDR unhooking | Malware cookbook content |
| Router/printer backdoors, `implant.sh`, Bjorn C2 | Hardware/implant deployment |
| Sliver / Havoc in install scripts | C2 framework provisioning |
| PoisonTap 2026 / Venice chat weaponized rewrites | USB MITM, CDN cache poisoning, cookie exfil, WS backdoors |
| `populate_cdn.sh`, `target_backdoor_*.js`, `pi_poisontap_2026.js` | CDN poisoning pipeline |

---

## Documentation converted to detection-only

When playbooks reference PHANTOM / SHADOW / GHOST / OCLeak / MIRCE / CitrixBleed:

- **Included:** MITRE mapping, Sigma rules, hunting steps, fingerprint troubleshooting, cleanup checklists
- **Excluded:** Runnable exploit one-liners, implant usage examples, obfuscation deployment tips, systemd backdoor templates

See:

- `docs/RED_TEAM_ADVANCED_PLAYBOOK.md` §3–6
- `docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md`
- `docs/NETWORK_2026_GUIDE.md` §4

---

## Quick audit

If a file contains any of the following, it does **not** belong in this repo:

- `CreateRemoteThread`, process hollowing payloads, shellcode hex blobs
- C2 listener bind commands on target hosts
- Persistence `ExecStart` pointing at implant scripts
- Exploit buffer-size tuning or SSRF/RCE trigger payloads
- `pyarmor` / implant obfuscation deployment steps

Authorized post-exploit work: **Cobalt Strike, Sliver, Metasploit, Atomic Red Team** under written ROE in isolated lab or scoped engagement.
