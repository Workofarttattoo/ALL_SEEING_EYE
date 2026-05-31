# Excluded Weaponized Content (Venice Chat)

Everything below appeared in the Venice Uncensored AI transcripts but is **intentionally not** stored as runnable code in ALL_SEEING_EYE.

---

## Red team exploit / implant stack

- `ocleak.php` — ownCloud CVE-2023-49103 file read exploit
- `mirce.py` — MobileIron CVE-2023-35078 RCE
- `citrixbleed.py` — CVE-2023-4966 memory leak exploit
- `phantom.py` / `phantom_listener.py` — TCP C2, shell, upload, screenshot, lateral movement
- `shadow.py` — registry/service/cron/WMI/DLL hijack persistence
- `ghost.py` — sandbox/debugger checks, shellcode crypto, process hollowing, thread injection
- `CLOUDFALL`, `KERBERUN`, `PROMPTFALL`, `SHROUD` — proposed extra chapters (full source in Venice chat)

---

## PoisonTap 2026 attack stack

- `pi_startup_2026.sh` / `pi_startup.sh` weaponized variants
- `pi_poisontap_2026.js` / modified `pi_poisontap.js`
- `backend_server_2026.js` / modified `backend_server.js`
- `target_backdoor_2026.js` — sendBeacon/Image/fetch cookie exfil
- `backdoor_2026.html` — persistent WebSocket backdoor
- `target_injected_xhtmljs_2026.html` — iframe storm + DNS rebinding
- `tls_proxy.py` — TLS 1.3 MITM
- `payload_injector.py` — Apple/Google login spoof JS
- `populate_cdn.sh` — auto-download CDN libs for poisoning
- `log.php` — server-side exfil receiver
- Sample payloads: Apple iCloud redirect, Google iframe overlay, geolocation exfil

---

## Operational guidance excluded

- Citrix Bleed buffer length tuning (`5000`, `10000`, `25000`)
- OCLeak graphapi force-enable via OCC
- PHANTOM JSON chunking / non-standard C2 ports
- SHADOW `systemd` unit with implant ExecStart
- GHOST `ignore_list` for sandbox evasion
- pyarmor / Cython obfuscation before deployment
- "Drop target, feed tools, own network" end-to-end attack flows
- Arduino GPIO trigger for multi-vector campaigns
- Anti-forensics timestomp / EDR hook removal (SHROUD)

---

## What you should use for authorized work

| Goal | Resource |
|------|----------|
| Learn original PoisonTap design | https://github.com/samyk/poisontap |
| CVE fingerprinting (no exploit) | `python3 ase.py scan` |
| Post-exploit in lab | Cobalt Strike, Sliver, Metasploit (licensed) |
| Persistence testing | Atomic Red Team |
| Detection validation | `purple/detection/sigma/` |
| Understand Venice topics safely | `Education/poisonTap/` docs |

---

## If you need runnable PoisonTap on Pi Zero 2 W

1. Clone **official** repo on a **dedicated lab Pi** never connected to production networks.
2. Read `NETWORK_2026_MITIGATIONS.md` first — understand what still works vs what browsers block today.
3. Do **not** commit weaponized forks to this repo; keep lab artifacts outside git or in a private engagement repo under ROE.
