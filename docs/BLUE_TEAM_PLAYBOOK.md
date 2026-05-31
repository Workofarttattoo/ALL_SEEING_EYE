# Blue Team Defensive Playbook

**ALL_SEEING_EYE Expected Red Team Engagement — Defensive Operations**

> Use this playbook when you are **defending** against an authorized red team exercise that mirrors ALL_SEEING_EYE recon: CVE fingerprinting, Shodan enrichment, mass scanning, and targeted exploitation of the 2025–2026 active CVE set documented in `data/cves.json`.

---

## 1. Engagement Assumptions

Your adversary (authorized red team) will likely:

| Phase | Expected activity | Your goal |
|-------|-------------------|-----------|
| Passive | Shodan/Censys lookups, DNS enumeration, OSINT | Reduce external exposure before Day 0 |
| Recon | `autorecon.py`, `mass_scan.sh`, port scans, banner grabs | Detect and alert on scan patterns |
| Fingerprint | CVE-specific HTTP/path probes (SAP, F5, n8n, Next.js, etc.) | Block or tarpit; log every hit |
| Exploitation | Target confirmed CVEs in scope | Patch, WAF, segment; contain fast |
| Post-exploit | LPE, credential abuse, lateral movement | EDR, tiered admin, hunt assumed breach |

**Mindset:** Assume they already have your Shodan footprint. Start from "what is indexed publicly?" not "will they find us?"

---

## 2. Pre-Engagement Hardening (T-7 to T-0)

### 2.1 External attack surface reduction

```bash
# Run YOUR copy of the toolkit against yourself first (authorized self-assessment)
python3 ase.py scan your-org.com --aggressive --shodan
python3 tools/shodan_recon.py hunt --org "Your Org Name" --count-only
python3 ase.py shodan domain your-org.com
```

Action items from results:

- [ ] Remove or VPN-gate every service not required on the public Internet
- [ ] Close MongoDB (27017), raw SSH (22), and admin panels from `0.0.0.0/0`
- [ ] Put F5 BIG-IP, Cisco ISE/FMC, Oracle OIM, and SAP NetWeaver **off the public internet** or behind IP allowlists
- [ ] Disable or auth-gate n8n `/form`, `/webhook`, and `/healthz` on any public instance
- [ ] Audit ShowDoc, MetInfo, Flowise — patch or decommission if unused

### 2.2 Patch priority queue (match red team CVE catalog)

| Priority | CVE / Asset | Defensive action |
|----------|-------------|------------------|
| P0 | CVE-2025-31324 / SAP NetWeaver | Patch SAP; block `/VisualComposer/`, `/VCFramework.wdvc` at WAF |
| P0 | CVE-2025-53521 / F5 BIG-IP | Upgrade F5; restrict `/mgmt/` to jump hosts only |
| P0 | CVE-2026-21992 / Oracle IEM | Patch OIM; no public `/oim/faces/` |
| P0 | CISCO-ISE / CISCO-FMC | Patch ISE/FMC; management VLAN only |
| P1 | CVE-2025-66478 / Next.js | Upgrade Next.js; disable `/_next/image` SSRF vectors; metadata IMDS blocked |
| P1 | CVE-2026-27493 / n8n | Upgrade n8n; disable public forms; require auth on API |
| P1 | CVE-2025-14847 / MongoDB | Patch MongoDB; bind to localhost; enable auth + TLS |
| P1 | CVE-2025-32433 / Erlang SSH | Patch Erlang/OTP SSH; rate-limit port 22; use keys only |
| P2 | CVE-2025-0520 / ShowDoc | Upgrade ≥2.8.7 or remove |
| P2 | CVE-2026-29014 / MetInfo | Upgrade CMS or WAF PHP injection rules |
| P2 | CVE-2025-59528 / Flowise | Patch; API keys rotated; not public |
| P2 | CVE-2026-20223 / Cisco REST | Patch IOS XE / RESTCONF; disable unused REST APIs |

### 2.3 Local / physical controls (if red team has insider or stolen laptop scenario)

| CVE | Control |
|-----|---------|
| CVE-2026-31431 / CVE-2026-43500 (Linux LPE) | Kernel patch cadence ≤30 days; EDR on Linux |
| CVE-2026-26117 (Azure Arc) | Audit ACLs on `AzureConnectedMachineAgent` directories |
| CVE-2025-62221 (MiniPlasma) | Windows patch; restrict Cloud Filter abuse paths |
| YELLOWKEY (BitLocker) | Secure Boot + TPM 2.0; disable WinRE USB boot; physical port control |

---

## 3. Detection Strategy

### 3.1 Recon detection — what ALL_SEEING_EYE looks like in logs

**Network (firewall / WAF / IDS):**

```
# Single-host CVE probe pattern (sequential paths within seconds)
/VisualComposer/VCFramework.wdvc
/tmui/login.jsp
/server/index.php
/api/v1/chatflows
/oim/faces/adf.task-flow
/_next/static/
/healthz
/admin/
```

**Alert:** Same source IP hits ≥3 known CVE fingerprint paths in 60 seconds → **High: CVE recon scan**

**Port scan (autorecon quick scan):**

```
Ports: 21,22,23,25,53,80,110,143,443,445,993,995,1723,3306,3389,
       5432,5900,5901,6379,8080,8443,9200,9300,27017,50000
```

**Alert:** SYN sweep touching ≥10 of these ports from one IP in 30s → **Medium: Port scan**

**Shodan passive indicator:** You won't see Shodan queries directly, but you CAN monitor for:

- Spike in traffic from known scanner ASNs (Shodan, Censys, ZoomEye crawlers)
- New hosts appearing in your Shodan org footprint → run weekly `hunt --org "Your Org" --count-only`

### 3.2 SIEM detection rules (Sigma-style logic)

**Rule: CVE Fingerprint Web Probe**

```
condition:
  event.category == "web"
  and http.request.method == "GET"
  and (
    url.path contains "VCFramework.wdvc" or
    url.path contains "tmui/login.jsp" or
    url.path contains "/oim/faces/" or
    url.path contains "/api/v1/chatflows" or
    url.path contains "uploadImg"
  )
  and count by src.ip over 5m >= 2
severity: high
```

**Rule: MongoDB Exposure Probe**

```
condition:
  network.destination.port == 27017
  and network.direction == "ingress"
  and source.ip not in $internal_scanner_allowlist
severity: critical
```

**Rule: Next.js SSRF Attempt**

```
condition:
  url.path contains "_next/image"
  and url.query contains "url=http"
  and (
    url.query contains "169.254.169.254" or
    url.query contains "127.0.0.1" or
    url.query contains "metadata"
  )
severity: critical
```

**Rule: Mass Scan Script (mass_scan.sh signature)**

```
condition:
  same src.ip
  and distinct url.path >= 5
  and time span <= 120s
  and user_agent contains "Mozilla/5.0"
  and no referrer
severity: medium
```

**Rule: n8n Unauthenticated Form Abuse**

```
condition:
  url.path in ("/form", "/form/", "/webhook", "/webhook/")
  and http.request.method == "POST"
  and http.response.status in (200, 500)
  and not authenticated
severity: high
```

### 3.3 EDR / host-based hunts

Run daily during engagement window:

| Hunt | Query / check |
|------|----------------|
| New web shells | Files created in web root with `.jsp`, `.php`, `.aspx` in last 24h |
| Suspicious upload | POST to `upload`, `uploadImg`, `VCFramework` paths followed by GET to new file |
| LPE attempts | `gcc`/`cc` invoked by non-dev users; AF_ALG socket creation spikes |
| Azure Arc tampering | Changes under `C:\Program Files\AzureConnectedMachineAgent\` |
| Credential access | `lsass.exe` access, `mimikatz`-like CLI patterns (if red team escalates) |

---

## 4. Response Playbooks by Scenario

### Scenario A: CVE fingerprint scan detected

1. **Identify** source IP — red team IP in ROE, or unknown?
2. **Block** at WAF/firewall if out of scope or excessive noise
3. **Pull** WAF logs for full path list — map to `data/cves.json`
4. **Verify** each probed service — patched? still exposed?
5. **Ticket** owners for any service that answered affirmatively
6. **Notify** red team liaison if in-scope (they may want you to leave it open)

### Scenario B: Successful exploitation suspected (RCE)

1. **Isolate** host at network layer (ACLS, EDR network containment)
2. **Preserve** memory if possible; snapshot VM
3. **Kill** suspicious processes; block C2 egress (unknown IPs, port 4444, etc.)
4. **Rotate** credentials on affected tier and adjacent systems
5. **Hunt** same IoCs across fleet (file hash, URI path, process name)
6. **Document** timeline for purple team debrief

### Scenario C: Shodan exposure discovered mid-engagement

1. Run `python3 tools/shodan_recon.py host <your-ip> --history`
2. Compare Shodan banners to intended config — anything unexpected?
3. Emergency patch or take offline services with `vulns[]` tags
4. Request Shodan block (org opt-out) for future — post-engagement cleanup

### Scenario D: Insider / local LPE path

1. Confirm patch level for kernel / Windows Cloud Filter
2. Restrict user to standard tier; force password reset
3. Hunt for new scheduled tasks, services, Run keys
4. Review Azure Arc agent permissions if cloud-joined

---

## 5. Defensive Architecture Checklist

```
Internet
   │
   ▼
[WAF] ── rate limit, geo block, CVE path deny rules
   │
   ▼
[Reverse Proxy / CDN] ── hide Server headers, strip X-Powered-By
   │
   ▼
[App Tier] ── no direct admin APIs; SSRF egress blocked to 169.254.0.0/16
   │
   ▼
[Data Tier] ── MongoDB/DB not routable from DMZ; auth required
   │
   ▼
[Mgmt Network] ── F5 / Cisco / SAP / Oracle admin — jump box + MFA only
```

**IMDS hardening (critical for Next.js SSRF chain):**

- AWS: IMDSv2 required, hop limit = 1
- Block egress to `169.254.169.254` from app subnets at firewall

---

## 6. Monitoring Dashboard (Engagement Week)

Track these metrics daily:

| Metric | Target |
|--------|--------|
| Critical CVE services internet-exposed | 0 |
| Shodan `vulns[]` on org assets | 0 |
| Unresolved P0 alerts from fingerprint rules | 0 |
| Mean time to contain (MTTC) test incidents | <30 min |
| WAF blocks on CVE probe paths | trending (expected during red team) |

---

## 7. Communication & ROE

- [ ] Confirm red team source IP ranges and scanner accounts
- [ ] Define "call red" threshold — e.g., production DB touched = immediate pause
- [ ] Daily blue/red sync (15 min) during active phase
- [ ] Single Slack/Teams channel for IOC sharing
- [ ] Legal/comms pre-approved statement if scan triggers customer alert

---

## 8. Post-Engagement Blue Deliverables

1. **Detection gap report** — which red team actions fired zero alerts?
2. **Patch verification** — re-run `ase scan --shodan` on all external assets
3. **Rule tuning** — reduce false positives on mass_scan signatures
4. **Shodan remediation** — confirm org footprint matches intent
5. **Lessons learned** — feed into purple team backlog

---

## 9. Quick Reference — Block These at WAF (If Not Business-Required)

```
/VisualComposer/*
/VCFramework.wdvc*
/tmui/*
/mgmt/*
/oim/faces/*
/server/index.php?s=/api/page/uploadImg
/api/v1/chatflows
/_next/image?url=*
/form
/webhook
```

---

## 10. Toolkit Cross-Reference

Run the same tools the red team uses — on yourself, first:

```bash
python3 ase.py scan your-domain.com --aggressive --shodan
python3 ase.py local                                    # lab jump host audit
bash scripts/mass_scan.sh your_external_hosts.txt
```

Compare output to your SIEM. Every **finding** in the JSON report should either:

- Be **patched and unreachable**, or
- **Generate an alert** when probed again.

See also: [RED_TEAM_PLAYBOOK.md](RED_TEAM_PLAYBOOK.md) | [PURPLE_TEAM_PLAYBOOK.md](PURPLE_TEAM_PLAYBOOK.md)
