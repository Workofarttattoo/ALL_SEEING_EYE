# Purple Team Playbook

**ALL_SEEING_EYE — Collaborative Attack & Defense Operations**

> Purple team = red executes, blue detects, both improve together in **controlled loops**. This playbook merges tactics from [BLUE_TEAM_PLAYBOOK.md](BLUE_TEAM_PLAYBOOK.md) and [RED_TEAM_PLAYBOOK.md](RED_TEAM_PLAYBOOK.md) into a single exercise cadence.

---

## 1. What Purple Team Is (Here)

| Team | Role in this exercise |
|------|------------------------|
| **Red** | Executes ALL_SEEING_EYE recon + scoped attack techniques |
| **Blue** | Monitors, detects, responds — does NOT warn red before alerts fire |
| **Purple lead** | Facilitates loops, scores detection coverage, manages scope |

**Not** a tabletop-only exercise. **Not** red hiding from blue. The value is **measuring the gap** between action and alert.

---

## 2. Exercise Structure

```
Week 0          Week 1              Week 2              Week 3
────────        ──────              ──────              ──────
Setup &         Loop 1–3            Loop 4–6            Closeout
baselines       (recon → detect)    (exploit → contain)  & metrics
```

### Loop template (repeat 6×)

```
┌──────────────────────────────────────────────────────────────┐
│  LOOP N — 4 hour block                                       │
├──────────────────────────────────────────────────────────────┤
│  T+0:00  Purple brief — red announces technique category     │
│  T+0:15  Red executes (blue blind to exact target/path)      │
│  T+1:00  Blue hunts — open SIEM tickets                      │
│  T+2:00  Timeout — purple calls "reveal"                     │
│  T+2:15  Joint debrief — detected? contained? MTTC?          │
│  T+3:00  Blue deploys new rule / red notes evasion (ROE)     │
│  T+4:00  Log loop scorecard                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Pre-Exercise Setup (Week 0)

### 3.1 Shared artifacts

Both teams use the same repo:

```bash
git clone <ALL_SEEING_EYE>
pip install -r requirements.txt
export SHODAN_API_KEY="..."   # shared or separate keys per ROE
```

| Artifact | Owner | Location |
|----------|-------|----------|
| CVE catalog | Shared | `data/cves.json` |
| Shodan dorks | Shared | `data/shodan_dorks.json` |
| Scope list | Purple lead | `exercise/scope.txt` |
| IOC log | Red → Purple | `exercise/ioc_log.json` |
| Detection scorecard | Blue → Purple | `exercise/detection_matrix.csv` |
| Loop schedule | Purple lead | `exercise/loop_schedule.md` |

### 3.2 Baseline measurements

**Red runs (authorized self-scan of scope):**

```bash
python3 tools/shodan_recon.py hunt --net $SCOPE_CIDR --count-only -o baselines/shodan_count.json
cat exercise/scope.txt | xargs -P3 -I{} python3 ase.py scan {} --shodan -o baselines/day0/
```

**Blue runs:**

- Export current SIEM rule count for CVE path probes
- Shodan org snapshot — `python3 tools/shodan_recon.py hunt --org "Target" --count-only`
- Document MTTC from last IR drill

**Purple records baseline score:**

| Metric | Day 0 value |
|--------|-------------|
| Internet-exposed P0 CVE services | |
| Shodan vuln-tagged hosts in scope | |
| Active SIEM rules for CVE fingerprints | |
| Historical MTTC (minutes) | |

---

## 4. Purple Team Loops — Scenario Pack

Each loop pairs a **red action** (from ALL_SEEING_EYE toolkit) with **blue expectations**.

---

### Loop 1: Passive Shodan recon

| | |
|---|---|
| **Red** | `shodan hunt --org "Target" --count-only` then `shodan host <ip>` on top 3 hits |
| **Blue goal** | Identify which assets appear in Shodan; verify org opt-out process |
| **Detection** | N/A (passive) — blue validates exposure inventory matches Shodan |
| **Success** | 100% of Shodan hits accounted for in CMDB |
| **Gap signal** | Unknown host in Shodan not in CMDB |

---

### Loop 2: Mass CVE fingerprint (`mass_scan.sh`)

| | |
|---|---|
| **Red** | `bash scripts/mass_scan.sh exercise/scope.txt` from registered scanner IP |
| **Blue goal** | Alert within 5 min on port scan + multi-path web probe |
| **Detection rules** | Port scan (≥10 ports/30s); CVE path probe (≥3 paths/60s) |
| **Success** | Both rules fire; ticket auto-created |
| **Improve** | Blue adds missing paths from `data/shodan_dorks.json` |

---

### Loop 3: Single-target deep scan + Shodan enrich

| | |
|---|---|
| **Red** | `python3 ase.py scan target --aggressive --shodan` |
| **Blue goal** | Correlate active scan with subsequent Shodan-enriched findings in report |
| **Detection** | Sequential CVE checks + DNS resolution spike |
| **Success** | Blue reconstructs red's JSON report from logs alone |
| **Purple metric** | Log completeness score (0–100%) |

---

### Loop 4: Next.js SSRF probe (CVE-2025-66478)

| | |
|---|---|
| **Red** | Request `/_next/image?url=http://169.254.169.254/&w=100` — detection test only |
| **Blue goal** | Block + alert on metadata SSRF pattern |
| **Detection** | Critical: `_next/image` + `169.254.169.254` in query |
| **Success** | WAF block + SIEM alert before response returns metadata |
| **Improve** | Confirm IMDSv2 + hop limit on app subnet |

---

### Loop 5: MongoDB exposure (CVE-2025-14847)

| | |
|---|---|
| **Red** | Port check 27017 from external scanner (no auth attempt) |
| **Blue goal** | Critical alert on ingress 27017 |
| **Detection** | Firewall deny + SIEM if connection attempted |
| **Success** | Zero successful connections; alert on SYN |
| **Improve** | Close port or VPN-only if business requires Mongo |

---

### Loop 6: n8n / workflow platform (CVE-2026-27493)

| | |
|---|---|
| **Red** | GET `/healthz`, POST `/form` with benign JSON — no exploit payload |
| **Blue goal** | Detect unauthenticated workflow surface |
| **Detection** | `/healthz` returns n8n + public `/form` POST without auth |
| **Success** | Alert + ticket to app owner same day |
| **Improve** | Auth-gate or decommission public n8n |

---

### Loop 7: Local LPE indicator (if foothold provided)

| | |
|---|---|
| **Red** | Purple provides red a **lab VM** low-priv shell; run `python3 ase.py local` |
| **Blue goal** | EDR alert on kernel exploit primitives or suspicious `gcc` |
| **Detection** | AF_ALG socket, privilege change, new root process |
| **Success** | EDR catches before priv escalation (if red attempts approved PoC) |
| **Scope** | Lab VM only — never production |

---

### Loop 8: Full chain simulation (capstone)

| | |
|---|---|
| **Red** | Passive Shodan → autorecon → one approved exploitation PoC → stop at proof |
| **Blue goal** | Detect at earliest phase; contain before lateral movement |
| **Purple scores** | Time-to-detect per phase, MTTC, communication quality |
| **Debrief** | Full timeline on whiteboard — red and blue fill gaps together |

---

## 5. Joint Tactics Matrix

How red and blue use the **same CVE data** differently:

| CVE | Red tactic (this repo) | Blue counter | Purple validation |
|-----|------------------------|--------------|-------------------|
| CVE-2025-31324 SAP | `autorecon` SAP paths | WAF deny `/VisualComposer/` | Re-scan post-WAF |
| CVE-2025-53521 F5 | fingerprint `/tmui/` | mgmt VLAN only | Shodan confirms closed |
| CVE-2025-66478 Next.js | SSRF probe URL | block IMDS egress | loop 4 replay |
| CVE-2025-14847 MongoDB | port 27017 in scan | firewall deny | `nc` fails externally |
| CVE-2026-27493 n8n | `/healthz` + `/form` | auth required | form returns 401 |
| CVE-2026-21992 Oracle OIM | `/oim/faces/` probe | remove public route | autorecon clean |
| CISCO-ISE | `/admin/` fingerprint | jump host only | Shodan count = 0 |
| CVE-2025-32433 Erlang SSH | banner on :22 | patch + rate limit | banner gone |
| Linux LPE | `ase local` on foothold | EDR + kernel patch | local scan clean |

---

## 6. Detection Scorecard (Purple Maintains)

After each loop, score:

| Loop | Technique | Red start | Blue alert | Delta (min) | Contained? | Rule added? |
|------|-----------|-----------|------------|-------------|------------|-------------|
| 1 | Shodan passive | — | — | — | N/A | Inventory |
| 2 | mass_scan | 10:00 | 10:04 | 4 | — | Y |
| 3 | autorecon+shodan | 11:00 | 11:02 | 2 | — | N |
| 4 | Next.js SSRF | 14:00 | 14:00 | 0 | Y | Y |
| … | | | | | | |

**Target metrics by end of exercise:**

| KPI | Target |
|-----|--------|
| Detection rate (loops with alert) | ≥80% |
| Mean time to detect (active loops) | ≤5 min |
| Mean time to contain (exploit loops) | ≤30 min |
| P0 CVE services still internet-exposed | 0 |
| New/ch tuned SIEM rules | ≥5 |

---

## 7. Flip-Sides Protocol

When teams **swap roles** mid-exercise:

### Blue → Red flip

1. Purple announces flip 24h in advance
2. Former blue shares which rules they deployed (category only, not exact signatures)
3. New red re-runs baseline Shodan count
4. New red registers scanner IPs with SOC
5. Loops 1–3 repeat — compare detection rate to round 1

### Red → Blue flip

1. Former red delivers complete IOC log: `exercise/ioc_log.json`
2. New blue has 4h to deploy detections before next loop
3. Third party (purple lead) runs `mass_scan.sh` as validation — did new blue detect it?

**Purple rule:** Flips test **adaptability**, not surprise. Both sides share the CVE catalog — the game is closing gaps fast.

---

## 8. Collaborative Commands

Both teams run these; results go in shared `exercise/` folder:

```bash
# Shared baseline
python3 ase.py cves --section remote > exercise/cve_list.txt
python3 ase.py shodan dorks > exercise/shodan_dorks.txt

# Red — log every action
echo "$(date -Is) mass_scan scope.txt" >> exercise/red_log.txt
bash scripts/mass_scan.sh exercise/scope.txt

# Blue — validate detections
python3 ase.py scan <target_from_red_log> --shodan   # replay red action
# Compare JSON findings to SIEM queries

# Purple — score
python3 -c "
import json, glob
reports = glob.glob('reports/*.json')
print(f'Reports generated: {len(reports)}')
"
```

---

## 9. Communication Cadence

| Meeting | When | Attendees | Output |
|---------|------|-----------|--------|
| Kickoff | Week 0 | All + exec sponsor | Scope sign-off |
| Loop brief | Each loop start | Purple + red | Technique category announced |
| Loop debrief | Each loop +2h15 | All | Scorecard row updated |
| Daily sync | 09:00 | Red/blue leads + purple | Blockers, IOC handoff |
| Flip briefing | Flip day -1 | All | Role swap rules |
| Closeout | Week 3 | All + exec | Final metrics, roadmap |

---

## 10. Deliverables (Purple Owns)

1. **Detection coverage map** — CVE × rule × tested (Y/N)
2. **MTTD/MTTC trend** — loop-by-loop chart
3. **Shodan before/after** — `hunt --count-only` snapshots
4. **Prioritized remediation backlog** — P0/P1/P2 with owners
5. **Rule pack export** — Sigma/KQL rules blue tuned during exercise
6. **Next exercise date** — recommended 90-day re-test

---

## 11. Sample Loop Schedule (2-Week Sprint)

| Day | Loop | Red action | Blue focus |
|-----|------|------------|------------|
| Mon | 1 | Shodan passive inventory | CMDB gap analysis |
| Mon | 2 | mass_scan.sh | Port + path alerts |
| Tue | 3 | autorecon --shodan | Log correlation |
| Tue | 4 | Next.js SSRF probe | WAF + IMDS |
| Wed | **FLIP** | Teams swap | IOC handoff |
| Wed | 5 | MongoDB port probe | Firewall rules |
| Thu | 6 | n8n surface check | AppSec ticket |
| Fri | 7 | Local LPE (lab VM) | EDR tuning |
| Mon | 8 | Full chain capstone | IR + comms test |
| Tue | — | Closeout debrief | Final report |

---

## 12. Ethics & Scope Guardrails

- Purple lead has **veto power** on any loop
- Either team can call **"PAUSE"** — exercise stops immediately
- No real PII in findings — synthetic flags only
- Shodan hunts **must** include scope filter (`org:`, `net:`, `hostname:`)
- Exploitation loops require **written approval per target**

---

## 13. Playbook Index

| Document | When to use |
|----------|-------------|
| [RED_TEAM_HANDBOOK.md](RED_TEAM_HANDBOOK.md) | CVE reference + tool commands |
| [RED_TEAM_PLAYBOOK.md](RED_TEAM_PLAYBOOK.md) | You are red — full engagement |
| [BLUE_TEAM_PLAYBOOK.md](BLUE_TEAM_PLAYBOOK.md) | You are blue — defend & detect |
| [PURPLE_TEAM_PLAYBOOK.md](PURPLE_TEAM_PLAYBOOK.md) | You are facilitating — this doc |
| [PURPLE_TEAM_HANDBOOK.md](PURPLE_TEAM_HANDBOOK.md) | Detection rules, hunting, IR, script index |
| [SHODAN.md](SHODAN.md) | Passive intel for all teams |

```bash
python3 ase.py playbook blue
python3 ase.py playbook red
python3 ase.py playbook purple
python3 ase.py handbook purple
python3 ase.py scripts
```
