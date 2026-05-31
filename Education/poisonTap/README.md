# PoisonTap — Educational Reference (Venice Chat Archive)

This folder documents **Samy Kamkar's PoisonTap** research and the **Venice Uncensored AI chat** that explored modernizing it for Raspberry Pi Zero 2 W. It is for **authorized security education, purple-team planning, and defensive hardening** only.

**Official source (research):** https://github.com/samyk/poisontap  
**Original write-up:** https://samy.pl/poisontap/

## What this folder contains

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Reverse-engineered breakdown of original repo components |
| [JS_CDN_CACHE.md](JS_CDN_CACHE.md) | What the `/js/` directory is and why it exists |
| [NETWORK_2026_MITIGATIONS.md](NETWORK_2026_MITIGATIONS.md) | Why 2026 networks behave differently; blue-team controls |
| [VENICE_CHAT_INDEX.md](VENICE_CHAT_INDEX.md) | Topic index of the Venice conversation |
| [EXCLUDED_WEAPONIZED.md](EXCLUDED_WEAPONIZED.md) | Everything from Venice chat **not** stored as runnable code |

## What this folder does NOT contain

- Modernized `pi_poisontap_2026.js`, backdoors, cookie exfil payloads, CDN poisoners
- PHANTOM / SHADOW / GHOST / OCLeak / MIRCE exploit source
- Deploy scripts, `populate_cdn.sh`, or C2 listeners

See repo-wide policy: `docs/EXCLUDED_CONTENT.md`

## Related ALL_SEEING_EYE assets

```bash
python3 ase.py playbook blue          # Defensive playbook
python3 ase.py handbook purple        # Detection handbook
python3 ase.py playbook advanced      # TTP detection mapping (not exploits)
cat docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md
cat purple/detection/sigma/c2_beacon_pattern.yml
```

## Lab use (authorized only)

If you need hands-on PoisonTap research:

1. Use Samy Kamkar's **official repo** in an isolated lab (no production USB ports).
2. Pair with full-disk encryption + browser closed + USB disabled on test targets.
3. Document findings in `exercise/detection_matrix.csv` for purple debrief.
