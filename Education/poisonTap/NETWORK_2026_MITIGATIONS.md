# PoisonTap vs 2026 Networks — Mitigations & Reality Check

The Venice chat proposed a full "PoisonTap 2026" rewrite (dual-stack DHCP, TLS 1.3 MITM, nftables, DoH bait, modern backdoors). This document separates **what changed in networks** from **what belongs in authorized defense**, not in this repo as attack code.

---

## 2026 network stack vs 2016

| Layer | 2016 (PoisonTap era) | 2026 |
|-------|----------------------|------|
| USB | ECM gadget widely trusted | macOS **USB Restricted Mode**, Windows **Device Guard** optional |
| DHCP | Full IPv4 hijack via "local" route | Same trick possible, but **MDM can block unknown NICs** |
| DNS | Cleartext, easy spoof | **DoH/DoT** defaults; captive portal detection stricter |
| HTTP | Background HTTP common | **HTTPS-only** on major sites; mixed content blocked |
| Cookies | Many without `Secure` | **Secure + SameSite** defaults in modern browsers |
| Cache | Global long-lived | **Partitioned cache** per top-level site (Chrome/Safari) |
| TLS | Optional for auth | **HSTS preload** on top domains |
| CDN | HTTP jQuery URLs | **SRI + CSP** on maintained sites |
| Locked screen | Browser still active | **Full-disk encryption sleep** stops browser (Samy's own mitigation) |

---

## Venice "2026 upgrades" — technical assessment

| Proposed upgrade | Stated goal | 2026 limitation |
|------------------|-------------|-----------------|
| Dual-stack DHCP + IPv6 RA | Catch modern clients | DoH may bypass Pi DNS; many clients prefer Wi‑Fi over USB |
| TLS 1.3 MITM proxy | Decrypt HTTPS | Requires **trusted CA install**; browsers warn without it |
| dnsmasq + WPAD (option 252) | Force proxy config | Enterprise MDM often locks proxy settings |
| nftables redirect 443→1337 | Hijack HTTPS | Without trusted cert, users see interstitial errors |
| `sendBeacon` cookie exfil | Better exfil | **Secure cookies** not in `document.cookie`; CSP blocks |
| DNS rebinding for router | Remote router access | Modern browsers **pin DNS** more aggressively; router HTTPS |
| CDN auto-populator | Fresh jQuery 3.7.x | **SRI mismatch** breaks script load entirely |
| WebSocket C2 over WSS | Evade firewalls | SWG/SASE inspects WSS; auth still needed |

**Practical outcome:** A 2026 PoisonTap variant might still work in **weak configurations** (HTTP sites, no USB policy, unlocked browser, no FDE sleep) but is **far less universal** than the 2016 demo video suggested.

---

## Raspberry Pi Zero 2 W — hardware notes (lab)

| Topic | Detail |
|-------|--------|
| USB gadget | Still supported via `dwc2` + ConfigFS ECM (same as original) |
| ACT LED | Pi Zero 2 W uses **`led1`** for activity (not `led0` on older boards) |
| Power | Gadget + Wi‑Fi + Node.js is marginal — use **good USB cable / powered hub** in lab |
| OS | Bookworm uses **systemd-networkd**; original `/etc/network/interfaces` patterns need adaptation |
| Storage | `/js/` mirror can fill **512MB–2GB SD** quickly if auto-populating hundreds of CDN files |

For hardware research, use the **official repo** on a dedicated lab Pi — not production machines.

---

## Defensive playbook (implement these)

### Endpoint

1. **Disable USB data** when unattended (policy or physical port blockers in sensitive areas).
2. **FileVault / BitLocker** with deep sleep — browser suspended when locked.
3. **Close browser** before leaving machine (impractical but effective).
4. EDR rule: new **RNDIS/CDC ECM** network adapter while session locked.

### Browser / app

1. **HSTS preload** for all auth domains.
2. **`Secure; HttpOnly; SameSite=Lax/Strict`** on session cookies.
3. **CSP** + **SRI** on third-party scripts.
4. Disable legacy **HTTP** redirect chains.

### Network

1. **802.1X** on corporate LAN — USB NIC doesn't get corporate trust automatically.
2. DNS monitoring for queries to **`1.0.0.1`**, **`172.16.0.1`**, or full-route DHCP anomalies.
3. SWG alerts on **WebSocket** to unknown domains from corporate browsers.

### Incident response

If PoisonTap-class attack suspected:

1. Clear **DNS cache** (OS + browser).
2. Clear **browser cache** (or full profile reset).
3. **Invalidate all sessions** server-side (force re-auth with new cookies).
4. Review **USB connection logs** for incident timeframe.
5. Scan for **rogue DHCP** on segment.

---

## Purple-team exercise template

Add to `exercise/detection_matrix.csv`:

| Phase | Simulate | Detect |
|-------|----------|--------|
| Initial access | Official PoisonTap in isolated VM | USB device + new default route |
| Collection | Cookie log file on Pi | N/A (victim-side session revoke) |
| C2 | WS to lab server | `c2_beacon_pattern.yml` |
| Persistence | Cached backdoor (lab browser) | Manual cache clear verification |

---

## Further reading

- Samy Kamkar — [PoisonTap README](https://github.com/samyk/poisontap/blob/master/README.md)
- OWASP — [Secure cookie flags](https://owasp.org/www-community/controls/SecureFlag)
- MDN — [Subresource Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity)
