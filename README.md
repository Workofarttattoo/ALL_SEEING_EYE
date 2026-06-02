# DIVINE SIGNAL

A modern, RISC-V powered network exploit and signal analysis platform for the Sipeed Smarthome UI panel.

"In His Grace, we are free."

## 1. Platform Comparison: RPi 5 vs. Sipeed RISC-V
| Feature | Raspberry Pi 5 | Sipeed RISC-V (D1/BL808) |
|---------|----------------|---------------------------|
| Architecture | ARM A76 (Quad-Core) | RISC-V (Single/Triple-Core) |
| Speed | 2.4GHz | 480MHz - 1GHz |
| Form Factor | SBC | Integrated Touch Panel |
| Power Efficiency | Moderate | High (Ideal for Handheld) |
| Sniffing Support | Excellent (USB/PCIe) | Integrated (WiFi/BLE/Zigbee) |
| UI Framework | X11/Wayland | Waft (WebAssembly) |

## 2. Setup (Sipeed RISC-V Linux)
1. **Flash Linux**: Ensure your Sipeed panel is running a modern Linux kernel (5.x+) with ConfigFS enabled.
2. **Deploy Files**:
   - Copy `sipeed_startup_2026.sh` to `/usr/bin/divine_startup`.
   - Copy `waft_ui_dashboard.xml` and `waft_ui_dashboard.js` to your Waft app directory.
3. **Hardware Config**:
   - Run `chmod +x /usr/bin/divine_startup`.
   - Add `/usr/bin/divine_startup` to your init system (systemd/OpenRC).
4. **Sniffing Dependencies**:
   - Ensure `dnsmasq`, `nftables` (or `iptables`), and `node.js` are installed.

## 3. Hardware & Shielding
See [hardware_guide.md](hardware_guide.md) for detailed instructions on:
- PCB pruning to reduce EMI.
- RF quarantine using soldered shielding cans.
- Designing a curved, handheld "palm-perfect" enclosure.

## 4. Spiritual Intent
This project is dedicated to the glory of Yahweh. The design avoids occult or demonic patterns, focusing on angelic symmetry and order.

---
*Disclaimer: This tool is for educational and authorized testing purposes only.*
