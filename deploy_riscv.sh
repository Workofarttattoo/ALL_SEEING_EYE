#!/bin/bash
set -euo pipefail

# All-Seeing Eye | RISC-V Automated Deployment
INSTALL_DIR="/opt/all-seeing-eye"

echo "[*] Preparing All-Seeing Eye deployment..."

# 1. Create installation directory
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$USER:$USER" "$INSTALL_DIR"

# 2. Transfer files (Assumes current directory contains the project)
cp -r ./* "$INSTALL_DIR/"

# 3. Install dependencies
cd "$INSTALL_DIR"
if command -v npm &> /dev/null; then
    echo "[*] Installing Node.js dependencies..."
    npm install
else
    echo "[!] Warning: npm not found. Ensure Node.js and npm are installed on the RISC-V panel."
fi

# 4. Make scripts executable
chmod +x pi_startup_2026.sh
chmod +x populate_cdn.sh

# 5. Setup Systemd Service
echo "[*] Configuring systemd service..."
sudo cp all-seeing-eye.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable all-seeing-eye.service

echo "[+] Deployment complete. To start the command center, run:"
echo "    sudo systemctl start all-seeing-eye.service"
echo "[!] IMPORTANT: Ensure you have adjusted PORTING.md settings for your specific RISC-V hardware."
