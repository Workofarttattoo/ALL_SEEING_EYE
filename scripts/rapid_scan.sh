#!/bin/bash
# Rapid remote CVE identification — extended remote set
# Usage: ./rapid_scan.sh targets.txt

set -euo pipefail

TARGETS="${1:-}"
OUTPUT="remote_scan_$(date +%Y%m%d_%H%M%S)"

echo -e "\033[91m"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        🔴 ALL_SEEING_EYE RAPID REMOTE SCAN 🔴            ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "\033[0m"

if [[ -z "$TARGETS" || ! -f "$TARGETS" ]]; then
  echo "Usage: $0 <targets.txt>"
  exit 1
fi

mkdir -p "$OUTPUT"

while read -r TARGET; do
  [[ -z "$TARGET" ]] && continue
  echo -e "\n\033[94m[*] Target: $TARGET\033[0m"

  echo -e "\033[93m[*] Checking Oracle Identity Manager...\033[0m"
  if curl -sk --max-time 10 "$TARGET/oim/faces/adf.task-flow" \
      -H "User-Agent: Mozilla/5.0" | grep -qi "oracle\|identity\|adf"; then
    echo -e "\033[91m[!] ORACLE IEM FOUND\033[0m"
    echo "$TARGET - CVE-2026-21992" >> "$OUTPUT/oracle_iem.txt"
  fi

  echo -e "\033[93m[*] Checking n8n...\033[0m"
  if curl -sk --max-time 10 "$TARGET/healthz" | grep -qi "n8n"; then
    echo -e "\033[91m[!] N8N FOUND\033[0m"
    echo "$TARGET - n8n CVEs (27493, 27577, 21858)" >> "$OUTPUT/n8n.txt"
  fi

  echo -e "\033[93m[*] Checking Cisco ISE...\033[0m"
  if curl -sk --max-time 10 "$TARGET/admin/" | grep -qi "cisco.*ise\|identity services engine"; then
    echo -e "\033[91m[!] CISCO ISE FOUND\033[0m"
    echo "$TARGET - Cisco ISE RCE" >> "$OUTPUT/cisco_ise.txt"
  fi

  echo -e "\033[93m[*] Checking Cisco FMC...\033[0m"
  if curl -skI --max-time 10 "$TARGET/api/fmc_config/" | grep -qi "cisco\|fmc"; then
    echo -e "\033[91m[!] CISCO FMC FOUND\033[0m"
    echo "$TARGET - Cisco FMC RCE" >> "$OUTPUT/cisco_fmc.txt"
  fi

  echo -e "\033[93m[*] Checking SAP...\033[0m"
  if curl -sk --max-time 10 "$TARGET/VisualComposer/VCFramework.wdvc" | grep -qi "sap\|visualcomposer"; then
    echo "$TARGET - CVE-2025-31324" >> "$OUTPUT/sap.txt"
  fi

  echo -e "\033[93m[*] Checking F5...\033[0m"
  if curl -sk --max-time 10 "$TARGET/tmui/login.jsp" | grep -qi "f5\|big-ip"; then
    echo "$TARGET - CVE-2025-53521" >> "$OUTPUT/f5.txt"
  fi
done < "$TARGETS"

echo -e "\n\033[92m[+] Scan complete!\033[0m"
echo "[*] Results saved to: $OUTPUT/"
ls -la "$OUTPUT/" 2>/dev/null || true
