# Shodan Integration Guide

How ALL_SEEING_EYE uses Shodan's public index — and how to think about their data model without needing to "reverse engineer" anything secret.

## What Shodan Actually Is

Shodan continuously scans the public Internet and stores **banners** — the raw text responses from open ports (HTTP headers, SSH versions, TLS certs, database handshakes, etc.). It then **parses** those banners into searchable fields.

Nothing magical: it's aggregated public data from services that respond to unsolicited connections. Their value is scale, history, and structured parsing.

Official references:

- API docs: https://developer.shodan.io/api
- Search filters: https://developer.shodan.io/search/filters
- Python library (open source): https://github.com/achillean/shodan-python

## Shodan's Data Model (What We Mirror)

Every indexed host becomes a document with roughly this shape:

```
Host
├── ip_str, org, isp, asn, os, tags
├── ports[]                    # all seen ports
├── hostnames[], domains[]
├── vulns[]                    # CVE tags (paid tier for full coverage)
└── data[]                     # one banner per port/service
    ├── port, product, version, transport
    ├── data                   # raw banner text
    ├── http.title, http.server, http.html, http.component
    ├── ssl.jarm, ssl.cert.*
    └── _shodan.module         # which probe collected it
```

**Our approach:** map each CVE in `data/cves.json` to Shodan filter queries in `data/shodan_dorks.json`, then cross-reference banners during enrichment.

## Setup

```bash
pip install -r requirements.txt

# Get API key: https://account.shodan.io
export SHODAN_API_KEY="your_key_here"
# or copy .env.example → .env
```

Free accounts get limited query credits. Use `--count-only` on hunts to scout before burning credits.

## Commands

```bash
# List our CVE → Shodan query mappings (no API key needed)
python3 ase.py shodan dorks

# Full host profile from Shodan's index
python3 ase.py shodan host 8.8.8.8
python3 ase.py shodan host target.example.com -- -o reports/shodan_host.json

# Subdomain/DNS intel
python3 ase.py shodan domain example.com

# Hunt all CVE dorks (count first — cheap)
python3 tools/shodan_recon.py hunt --count-only
python3 tools/shodan_recon.py hunt --cve CVE-2025-53521 --limit 5

# Scope hunts to your engagement
python3 tools/shodan_recon.py hunt --cve CVE-2025-14847 --net 10.0.0.0/8
python3 tools/shodan_recon.py hunt --org "Acme Corp" --count-only

# Raw search
python3 ase.py shodan search 'product:"MongoDB" country:US' -- --count-only

# Enrich a normal scan with Shodan banners + vuln tags
python3 ase.py scan target.example.com --shodan
```

## Workflow: Shodan-First Recon

For authorized assessments, this sequence maximizes signal per API credit:

```bash
# 1. Count exposure globally or per-scope (cheap)
python3 tools/shodan_recon.py hunt --cve CVE-2025-53521 --count-only
python3 tools/shodan_recon.py hunt --org "Target Corp" --count-only

# 2. Pull subdomains Shodan already found
python3 tools/shodan_recon.py domain target.com -o reports/dns.json

# 3. Host profile before active scanning
python3 tools/shodan_recon.py host 203.0.113.10 --history

# 4. Active fingerprint + merge Shodan intel
python3 ase.py scan 203.0.113.10 --aggressive --shodan
```

## How We Built the Dork Catalog

Each entry in `data/shodan_dorks.json` follows Shodan's filter syntax:

| Filter | Example | Use |
|--------|---------|-----|
| `product:` | `product:"MongoDB"` | Parsed service name |
| `port:` | `port:27017` | Open port |
| `http.title:` | `http.title:"BIG-IP"` | HTML title |
| `http.html:` | `http.html:"__next"` | Body content |
| `http.component:` | `http.component:"Next.js"` | Wappalyzer-style detection |
| `vuln:` | `vuln:CVE-2024-1234` | Shodan CVE tag (membership) |
| `org:` | `org:"Amazon"` | WHOIS org |
| `net:` | `net:192.168.0.0/16` | CIDR scope |
| `hostname:` | `hostname:target.com` | DNS name |

We derived these by reading Shodan's [filter documentation](https://developer.shodan.io/search/filters) and matching fields our active scanners already fingerprint — not by decompiling anything.

## Enrichment Logic

When you pass `--shodan` to a scan, `lib/shodan_enrich.py`:

1. Resolves target → IP
2. Calls `api.host(ip)` for full historical banners
3. Merges Shodan ports into the port list
4. Maps banner fingerprints → CVE findings (same rules as `host_to_findings()`)
5. Surfaces Shodan `vulns[]` tags as HIGH confidence findings

## API Credit Tips

- **`count`** queries cost less than full **`search`**
- Use **`--count-only`** on hunts to map exposure before pulling matches
- Scope with `net:`, `org:`, or `hostname:` to stay in engagement bounds
- **`host(ip)`** lookup is one credit per IP — use before active scanning
- **`dns/domain`** is separate from host search — good for subdomain seeding

## What Shodan Gives You That Active Scanning Doesn't

| Capability | Active scan | Shodan |
|------------|-------------|--------|
| Historical banners | No | Yes (`--history`) |
| Pre-discovered subdomains | Manual | `dns/domain` |
| Global exposure counts | No | `count` + facets |
| CVE tags on hosts | Manual | `vulns[]` field |
| Org/ASN context | Partial | Full WHOIS index |
| Stealth | Noisy | Passive (already indexed) |

## Authorization

Shodan data is public, but **using it to target systems still requires authorization**. Scope hunts with `net:`, `org:`, or `hostname:` filters to assets in your rules of engagement.
