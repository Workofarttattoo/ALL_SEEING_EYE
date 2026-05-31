# Network Attack Surface 2026

**Modern recon for authorized assessments — ALL_SEEING_EYE companion guide**

> Assumes college-level networking. Focus: QUIC/HTTP3, DoH, WiFi 7, eBPF observability, stealth fingerprinting. This repo ships **detection and recon orchestration** — not malware, implants, or hardware backdoors.

```bash
python3 ase.py handbook network
python3 ase.py network example.com
bash scripts/install-recon-tools.sh
```

---

## Chapter 1: The 2026 Attack Surface

**What changed:**

| Layer | 2026 reality |
|-------|----------------|
| Transport | QUIC (UDP 443) carries most web/API traffic; TCP SYN scans miss it |
| DNS | DoH/DoT default in Zero Trust; plaintext DNS often internal-only |
| WiFi | 802.11be (WiFi 7) multi-link operation across 2.4/5/6 GHz |
| BLE | 5.4 — LE Audio, periodic advertising, connection subevents |
| Host | `nftables` + cgroups + eBPF; containers/K8s everywhere |

**Red team recon priority:** passive TLS/QUIC fingerprint → app-layer crawl → targeted ASE CVE checks → avoid noisy `nmap -sS` on WAF-protected edges.

**Blue team priority:** eBPF visibility, QUIC/DoH egress logging, BLE/WiFi rogue detection.

---

## Chapter 2: Stealth Recon Workflow (Authorized)

### 2.1 ASE-native (always available)

```bash
# Passive Shodan first
python3 tools/shodan_recon.py hunt --org "Target" --count-only
python3 ase.py shodan domain target.com

# Active fingerprint (CVE catalog)
python3 ase.py scan target.com --aggressive --shodan
python3 ase.py aura target.com

# Bulk
bash scripts/mass_scan.sh scope.txt
```

### 2.2 External modern scanners (optional)

Install via `bash scripts/install-recon-tools.sh` (ProjectDiscovery stack only):

```bash
# TLS / QUIC / ALPN fingerprint (prefer over nmap for edge targets)
tlsx -l targets.txt -json -o reports/tlsx.json

# Template-based misconfig (headers, exposed panels)
nuclei -t http/ -l urls.txt -json -o reports/nuclei.json

# JS-heavy SPA crawl
katana -u https://target.com -js-crawl -depth 3 -o reports/katana.txt
```

### 2.3 Orchestrated via ASE

```bash
python3 ase.py network target.com
python3 ase.py network --targets urls.txt --skip-external
```

Runs ASE scan + optionally tlsx/nuclei if installed.

### 2.4 Blue team — eBPF visibility (defensive)

```bash
sudo apt install bpftrace
# Sample: high-volume UDP/443 (QUIC)
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_sendto /args->fd > 2/ { @bytes[comm] = sum(args->len); }'
```

Use for **detection**, not covert implant deployment.

---

## Chapter 3: CVE Quick Reference (2024–2026)

Dummy rule: a CVE is a catalog ID for a known defect. We **fingerprint**, not exploit.

| CVE | Target | ASE detection | Patch direction |
|-----|--------|---------------|-----------------|
| CVE-2024-6387 | OpenSSH regreSSHion | SSH banner version parse | OpenSSH ≥9.8p2 |
| CVE-2024-47699 | GoAccess SSRF | GoAccess panel fingerprint | Upgrade GoAccess |
| CVE-2024-1086 | Linux nf_tables LPE | `ase local` kernel check | Kernel patch |
| CVE-2025-22876 | Tomcat path traversal | `/manager/html` fingerprint | Tomcat upgrade |

```bash
python3 ase.py cves --section remote
python3 ase.py cves --section local
```

Full catalog: `data/cves.json`

---

## Chapter 4: What This Repo Does NOT Include

The following from generic "hacker cookbooks" are **out of scope**:

| Category | Examples | Use instead (authorized ROE) |
|----------|----------|------------------------------|
| Malware / implants | Memory droppers, DNS C2, eBPF beacons | Licensed C2 (Sliver, CS) in lab only |
| EDR evasion | API unhooking, process hollowing code | Purple team validation + Sigma rules |
| Hardware backdoors | Router `rc.local` nc, printer G-code inject | Vendor firmware audit; physical security |
| Persistent sniffers | `implant.sh` beacon loops | NetFlow, Zeek, eBPF on monitored taps |

Detection mapping: `docs/ttps/POST_EXPLOIT_TTP_REFERENCE.md`  
Purple rules: `purple/detection/sigma/`

---

## Chapter 5: Detection — QUIC, DoH, BLE

### QUIC / HTTP3 egress

- Log UDP/443 volume per host; alert on sustained QUIC to unknown ASNs
- Compare `tlsx` ALPN=`h3` against allowlisted CDNs

### DNS-over-HTTPS exfil patterns

Sigma: `purple/detection/sigma/doh_exfil_pattern.yml`

- High-rate `dns.google/resolve` or `cloudflare-dns.com/dns-query` with long subdomain labels
- TXT query bursts from non-browser processes

### WiFi / BLE (physical engagement)

- Rogue AP: monitor for duplicate SSIDs, unexpected 6 GHz beacons
- BLE: scan for unexpected connectable devices in sensitive zones (`bleak` for **inventory**, not covert access)

---

## Chapter 6: Tooling Matrix

| Tool | Path / install | Role |
|------|----------------|------|
| ASE scan | `python3 ase.py scan` | CVE fingerprint |
| AURA | `python3 ase.py aura` | Subdomain + ports + CVE |
| Shodan | `python3 ase.py shodan` | Passive intel |
| tlsx | `scripts/install-recon-tools.sh` | TLS/QUIC enum |
| nuclei | same | Template misconfig |
| katana | same | Web crawl |
| network_recon | `tools/network_recon.py` | Orchestrator |
| bpftrace | apt | Blue eBPF |

Script index: `python3 ase.py scripts`

---

## Chapter 7: Recommended Assessment Flow

```
1. Shodan hunt (scoped)     →  exposure inventory
2. tlsx + nuclei (optional) →  TLS/API misconfigs
3. ase aura / scan          →  CVE fingerprint JSON
4. Purple debrief           →  detection_matrix.csv
5. Remediate + re-scan      →  confirm clean
```

---

## Related docs

| Doc | Command |
|-----|---------|
| Red handbook | `python3 ase.py handbook` |
| Advanced red playbook | `python3 ase.py playbook advanced` |
| Purple handbook | `python3 ase.py handbook purple` |
| Shodan guide | `docs/SHODAN.md` |
