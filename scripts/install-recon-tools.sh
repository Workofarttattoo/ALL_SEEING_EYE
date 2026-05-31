#!/bin/bash
# Install optional modern RECON tools (ProjectDiscovery stack)
# Does NOT install C2 frameworks, exploit kits, or implant tooling
set -euo pipefail

echo "[*] ALL_SEEING_EYE — recon tool installer (authorized use only)"

if ! command -v go >/dev/null 2>&1; then
  echo "[!] Go not found. Install: sudo apt install golang-go"
  exit 1
fi

export PATH="${PATH}:$(go env GOPATH)/bin"

install_go_tool() {
  local pkg="$1"
  echo "[*] go install ${pkg}@latest"
  go install "${pkg}@latest"
}

install_go_tool github.com/projectdiscovery/tlsx/cmd/tlsx
install_go_tool github.com/projectdiscovery/nuclei/v3/cmd/nuclei
install_go_tool github.com/projectdiscovery/katana/cmd/katana

if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y bpftrace 2>/dev/null || echo "[!] bpftrace install skipped (optional)"
fi

echo "[+] Installed to $(go env GOPATH)/bin"
echo "[+] Verify: tlsx -version && nuclei -version && katana -version"
echo "[*] Usage: python3 ase.py network target.com"
