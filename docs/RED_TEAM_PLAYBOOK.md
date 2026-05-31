# Red Team Engagement Playbook

**ALL_SEEING_EYE — Authorized Offensive Operations**

> Use when you **flip to red**. This playbook covers authorized recon, target selection, CVE-aligned attack paths, and reporting — aligned with the detection/fingerprint toolkit in this repo. Exploitation beyond proof-of-concept requires explicit ROE approval and licensed tooling.

---

## 1. Mission Objectives

Primary goals for this engagement:

1. **Validate** blue team detection of CVE-focused recon and exploitation
2. **Identify** internet-exposed instances of high-value CVE targets in scope
3. **Demonstrate** impact on unpatched services (with approval)
4. **Deliver** actionable findings mapped to `data/cves.json`

Success = documented attack path + blue team response time + remediation priority — not persistence or data theft unless explicitly scoped.

---

## 2. Rules of Engagement (ROE) Checklist

Before any action:

- [ ] Signed authorization letter / SOW with named systems and IP ranges
- [ ] Emergency contact and "stop" keyword agreed
- [ ] Production vs staging boundaries documented
- [ ] Exploitation vs detection-only mode confirmed
- [ ] Data exfiltration limits defined (if any)
- [ ] Hours of operation (e.g., 09:00–17:00 local only)
- [ ] Source IPs registered with blue team / SOC
- [ ] Shodan queries scoped to `org:`, `net:`, or `hostname:` in scope only

**Never** scan or exploit out-of-scope assets — including Shodan dorks without scope modifiers.

---

## 3. Engagement Phases

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Phase 0    │───▶│  Phase 1    │───▶│  Phase 2    │───▶│  Phase 3    │
│  Planning   │    │  Passive    │    │  Active     │    │  Reporting  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Phase 0: Planning (Day -3 to Day 0)

### 0.1 Intelligence gathering

```bash
# Scope-bound Shodan (passive — register with blue team)
export SHODAN_API_KEY="your_key"

python3 tools/shodan_recon.py hunt --org "Target Corp" --count-only
python3 tools/shodan_recon.py hunt --net 203.0.113.0/24 --count-only
python3 ase.py shodan domain target.com -o intel/dns.json
python3 ase.py shodan dorks    # review query catalog
```

Document:

- Subdomains from Shodan DNS
- Hosts with `vulns[]` tags
- Exposed ports: 27017, 443/mgmt, 50000 (SAP), 22

### 0.2 Target prioritization matrix

| Score | Criteria |
|-------|----------|
| +3 | Shodan `vulns[]` matches tracked CVE |
| +3 | Pre-auth RCE fingerprint (SAP, F5, OIM, n8n forms) |
| +2 | Admin panel internet-facing |
| +2 | No WAF / rate limiting observed |
| +1 | Staging/dev hostname pattern |
| -3 | Out of scope / production-critical (ROE deny) |

### 0.3 Build target list

```
targets/
├── passive_shodan.txt      # from hunt results
├── dns_subdomains.txt      # from shodan domain
├── confirmed_scope.txt     # ROE-approved only
└── priority_queue.txt      # scored targets
```

---

## Phase 1: Passive Recon (Day 1)

**Goal:** Map attack surface without triggering active scan alerts.

| Action | Tool | OPSEC |
|--------|------|-------|
| Org footprint count | `shodan hunt --count-only` | Low noise |
| Host profiles | `shodan host <ip>` | 1 credit/IP |
| DNS/subdomains | `shodan domain target.com` | Passive |
| Certificate transparency | crt.sh, etc. | External |
| GitHub/code leak search | Manual / OSINT | No touch target |

**Deliverable:** Passive intel report — no packets to target yet.

---

## Phase 2: Active Recon & Fingerprint (Day 2–3)

**Goal:** Confirm Shodan data; trigger blue detection (if testing detections).

### 2.1 Single-target deep scan

```bash
python3 ase.py scan https://target.in.scope --aggressive --shodan \
  --output-dir reports/day2/

python3 ase.py remote target.in.scope --output-dir reports/day2/
```

Review JSON report — map `findings[]` to exploitation candidates.

### 2.2 Mass fingerprint (controlled)

```bash
# Throttle parallelism per ROE — default xargs -P10 may be too loud
cat confirmed_scope.txt | xargs -P3 -I{} python3 tools/autorecon.py {} --aggressive

bash scripts/mass_scan.sh confirmed_scope.txt
bash scripts/rapid_scan.sh priority_queue.txt
```

**OPSEC during active phase:**

- Rotate source IP if ROE allows (residential proxy only if approved)
- Add jitter: `sleep $((RANDOM % 5 + 1))` between targets in custom wrappers
- Use `-P3` not `-P10` if blue asked for lower noise
- Register scanner User-Agent with SOC if using default

### 2.3 CVE-specific validation (detection-only in this repo)

For each HIGH confidence finding, manually validate:

| Finding | Validation step |
|---------|-----------------|
| SAP CVE-2025-31324 | Confirm VCFramework path returns SAP markers; do NOT upload |
| F5 CVE-2025-53521 | Confirm `/tmui/login.jsp`; mgmt API reachable? |
| Next.js CVE-2025-66478 | Check `/_next/image?url=http://169.254.169.254/` — SSRF reflection only |
| MongoDB CVE-2025-14847 | `nc -zv` port 27017; no data dump |
| n8n CVE-2026-27493 | `/healthz` returns n8n; form endpoint exists? |
| ShowDoc / MetInfo / Flowise | Title/body fingerprint match |

**Exploitation:** Use approved commercial framework (Metasploit module, vendor PoC in lab) only with written approval — not this repo.

---

## Phase 3: Exploitation & Post-Exploit (Day 4–5, if scoped)

Only if ROE permits active exploitation:

### 3.1 Remote exploitation priority

```
1. Pre-auth RCE (SAP, F5 mgmt, OIM, Cisco ISE, n8n forms)
2. Auth bypass (Cisco REST, Oracle ADF)
3. SSRF → cloud metadata (Next.js)
4. Info disclosure → cred reuse (MongoBleed)
```

### 3.2 Local / physical paths (if insider scenario in scope)

```bash
python3 ase.py local    # on foothold host — indicator scan only
```

| Path | When |
|------|------|
| Linux LPE (Copy Fail, Dirty Frag) | Shell as low-priv user on unpatched kernel |
| Azure Arc (CVE-2026-26117) | Cloud-joined Windows/Linux with weak agent ACLs |
| MiniPlasma (CVE-2025-62221) | Unpatched Win10/11 with Cloud Filter |
| YellowKey | Physical engagement only — USB boot scenario |

### 3.3 Post-exploit boundaries (typical ROE)

Allowed:

- Proof screenshot / `id` / `hostname`
- Single flag file read
- Network diagram of reachable segments

Not allowed (unless explicit):

- Ransomware simulation
- Destructive commands
- Real data exfiltration
- Persistence beyond engagement window
- Social engineering of non-participants

---

## Phase 4: Reporting (Day 5–6)

### 4.1 Finding template

```markdown
## FINDING-001: [CRITICAL] F5 BIG-IP Internet-Exposed Management

**CVE:** CVE-2025-53521
**Asset:** 203.0.113.50 (bigip.target.com)
**Discovered:** Shodan hunt + autorecon fingerprint
**Evidence:** /tmui/login.jsp accessible; iControl REST on 443
**Impact:** Unauthenticated RCE potential — full network gateway compromise
**Blue team detection:** [ YES / NO ] — rule "CVE Fingerprint Web Probe" fired at T+2min
**Recommendation:** Move mgmt to out-of-band; patch to fixed version; IP allowlist
**Repro:** python3 ase.py scan https://bigip.target.com --aggressive
```

### 4.2 Report sections

1. Executive summary (1 page)
2. Scope and methodology
3. Attack timeline (passive → active → exploit)
4. Findings by severity with CVE mapping
5. Detection validation matrix (red action vs blue alert)
6. Shodan exposure appendix (before/after)
7. Remediation priority queue

### 4.3 Detection validation matrix

| Red team action | Timestamp | Blue alert? | Rule name | Gap? |
|-----------------|-----------|-------------|-----------|------|
| mass_scan.sh on /24 | Day 2 10:15 | Yes | Port scan | No |
| SAP path probe | Day 2 10:16 | No | — | **YES** |
| Shodan host lookup | Day 1 | N/A | Passive | — |

---

## 5. Tool Quick Reference

```bash
# Passive
python3 tools/shodan_recon.py hunt --org "Target" --count-only
python3 ase.py shodan domain target.com

# Active fingerprint
python3 ase.py scan <target> --aggressive --shodan
bash scripts/mass_scan.sh targets.txt
bash scripts/rapid_scan.sh priority.txt

# Local (foothold)
python3 ase.py local

# Reference
python3 ase.py cves --section remote
python3 ase.py handbook
python3 ase.py playbook blue    # know what they're running
```

---

## 6. OPSEC & Legal

- All activity logged to `reports/` with timestamps
- Encrypt findings at rest
- Destroy client data per retention schedule
- Do not discuss engagement on Shodan-visible infrastructure
- If you hit out-of-scope asset — **stop, notify, document**

---

## 7. Handoff to Purple Team

After red delivery, provide blue with:

1. Complete IOC list (IPs, paths, timestamps, User-Agents)
2. Exact commands run (copy from shell history / reports)
3. Which findings were intentional detection tests
4. Recommended purple team replay schedule

See: [PURPLE_TEAM_PLAYBOOK.md](PURPLE_TEAM_PLAYBOOK.md)

---

## 8. Flip-Side Reminder

When you switch from blue to red:

- **Blue playbook** tells you exactly what they're watching for — use it to test gaps, not to evade responsibly-disclosed ROE
- Re-register your scanner IPs on flip day
- Reset mutual trust: blue may have deployed new rules overnight

See also: [BLUE_TEAM_PLAYBOOK.md](BLUE_TEAM_PLAYBOOK.md) | [RED_TEAM_HANDBOOK.md](RED_TEAM_HANDBOOK.md)
