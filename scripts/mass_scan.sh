#!/bin/bash
# Mass CVE fingerprint scanner — detection only
# Usage: ./mass_scan.sh targets.txt

set -euo pipefail

TARGETS="${1:-}"
OUTPUT_DIR="scan_results_$(date +%Y%m%d_%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "\033[91m"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           🔴 ALL_SEEING_EYE MASS SCANNER 🔴              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "\033[0m"

if [[ -z "$TARGETS" || ! -f "$TARGETS" ]]; then
  echo "Usage: $0 <targets.txt>"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"
TOTAL=$(wc -l < "$TARGETS")
CURRENT=0

while read -r TARGET; do
  [[ -z "$TARGET" ]] && continue
  CURRENT=$((CURRENT + 1))
  echo -e "\n\033[94m[$CURRENT/$TOTAL] Scanning: $TARGET\033[0m"

  OUT="$OUTPUT_DIR/${TARGET//\//_}.txt"
  IP=$(dig +short "$TARGET" 2>/dev/null | head -1 || true)
  echo "IP: ${IP:-unknown}" >> "$OUT"

  echo -e "\033[93m[*] Checking SAP NetWeaver...\033[0m"
  if curl -sk --max-time 10 "https://$TARGET/VisualComposer/VCFramework.wdvc" \
      -H "User-Agent: Mozilla/5.0" | grep -qi "sap\|visualcomposer"; then
    echo -e "\033[91m[!] SAP DETECTED: $TARGET\033[0m"
    echo "CVE-2025-31324: SAP FOUND" >> "$OUT"
  fi

  echo -e "\033[93m[*] Checking F5 BIG-IP...\033[0m"
  if curl -sk --max-time 10 "https://$TARGET/tmui/login.jsp" | grep -qi "f5\|big-ip"; then
    echo -e "\033[91m[!] F5 DETECTED: $TARGET\033[0m"
    echo "CVE-2025-53521: F5 FOUND" >> "$OUT"
  fi

  echo -e "\033[93m[*] Checking MetInfo CMS...\033[0m"
  if curl -sk --max-time 10 "http://$TARGET/" | grep -qi "metinfo\|content=\"metinfo\""; then
    echo -e "\033[91m[!] METINFO DETECTED: $TARGET\033[0m"
    echo "CVE-2026-29014: METINFO FOUND" >> "$OUT"
  fi

  echo -e "\033[93m[*] Checking ShowDoc...\033[0m"
  if curl -sk --max-time 10 "http://$TARGET/server/index.php" | grep -qi "showdoc"; then
    echo -e "\033[91m[!] SHOWDOC DETECTED: $TARGET\033[0m"
    echo "CVE-2025-0520: SHOWDOC FOUND" >> "$OUT"
  fi

  echo -e "\033[93m[*] Checking Next.js...\033[0m"
  if curl -skI --max-time 10 "https://$TARGET/" | grep -qi "next.js\|x-powered-by.*next"; then
    echo -e "\033[91m[!] NEXT.JS DETECTED: $TARGET\033[0m"
    echo "CVE-2025-66478: NEXTJS FOUND" >> "$OUT"
  fi

  echo -e "\033[93m[*] Checking Flowise AI...\033[0m"
  if curl -sk --max-time 10 "http://$TARGET/api/v1/chatflows" | grep -qi "flowise"; then
    echo -e "\033[91m[!] FLOWISE DETECTED: $TARGET\033[0m"
    echo "CVE-2025-59528: FLOWISE FOUND" >> "$OUT"
  fi

  echo -e "\033[93m[*] Checking n8n...\033[0m"
  if curl -sk --max-time 10 "http://$TARGET/healthz" | grep -qi "n8n"; then
    echo -e "\033[91m[!] N8N DETECTED: $TARGET\033[0m"
    echo "CVE-2026-27493: N8N FOUND" >> "$OUT"
  fi

  if [[ -n "${IP:-}" ]]; then
    echo -e "\033[93m[*] Checking MongoDB ports...\033[0m"
    if timeout 3 bash -c "cat < /dev/null > /dev/tcp/$IP/27017" 2>/dev/null; then
      echo -e "\033[91m[!] MONGODB OPEN: $TARGET:27017\033[0m"
      echo "CVE-2025-14847: MONGODB PORT 27017 OPEN" >> "$OUT"
    fi

    echo -e "\033[93m[*] Checking SSH...\033[0m"
    if timeout 3 bash -c "cat < /dev/null > /dev/tcp/$IP/22" 2>/dev/null; then
      echo -e "\033[91m[!] SSH OPEN: $TARGET:22\033[0m"
      echo "CVE-2025-32433: SSH PORT 22 OPEN" >> "$OUT"
    fi
  fi

  # Prefer Python autorecon when available for richer JSON output
  if command -v python3 >/dev/null 2>&1; then
    python3 "$ROOT_DIR/tools/autorecon.py" "$TARGET" --output-dir "$OUTPUT_DIR/json" >/dev/null 2>&1 || true
  fi
done < "$TARGETS"

echo -e "\n\033[92m[+] Scan complete! Results saved to: $OUTPUT_DIR/\033[0m"
echo -e "\n\033[91m=== VULNERABILITY SUMMARY ===\033[0m"
grep -l "CVE" "$OUTPUT_DIR"/*.txt 2>/dev/null | while read -r f; do
  echo -e "\n\033[93m$(basename "$f" .txt):\033[0m"
  grep "CVE" "$f" || true
done
