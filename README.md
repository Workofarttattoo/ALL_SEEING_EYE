# ALL_SEEING_EYE: Dual-Mode Occult-Cyberpunk Command Center

Optimized for Lichee RISC-V boards and 86mm Smart Home Panels.

## Features
- **Covert Mode:** Boots by default into a legitimate-looking WAFT Smart Home UI for inspection passing.
- **True Firmware:** Activated via a secret slider combination (Living Room at 66%) to "boot" into the All-Seeing Eye command center.
- **Neo-Occult Terminal:** 4K dashboard with engraver-style art, sacred geometry, and tribal sigils.
- **Aura Cleanser & Ghost Box:** Functional RF simulation and bio-resonance generators.
- **Subversive Zine:** Hidden "Illegal Thoughts" digital zine (Second 60s / 2066 theme).
- **RISC-V Optimized:** High-concurrency Node.js backend with async I/O.

## Deployment
1. Transfer files to the panel.
2. Run `./deploy_riscv.sh` to install and enable the autostart service.
3. The panel will now boot directly into the "Legitimate" home UI.

## Viewports

| Route        | Target                              | File                              |
|--------------|-------------------------------------|-----------------------------------|
| `/`          | Covert WAFT smart-home UI           | `waft_ui.html`                    |
| `/occult`    | Neo-Occult command center (square)  | `ui_4k_all_seeing_eye.html`       |
| `/round`     | Round-display variant (watch/dial)  | `ui_round_all_seeing_eye.html`    |
| `/zine`      | Hidden 2066 zine                    | `zine.html`                       |

The square `/occult` view is tuned for the **Sipeed Lichee RV 86mm panel** and similar 480×480 / landscape touchscreens.
The new `/round` view is tuned for round AMOLED dials (240×240, 466×466) and degrades cleanly on phones.

## Venice link (uncensored chat fallback)

Both `/occult` and `/round` ship a floating chat overlay that talks to Venice — used when the primary model refuses a question worth answering.

1. Copy `.env.example` → `.env` and paste your key:
   ```
   VENICE_API_KEY=your-real-key
   ```
   `.env` is gitignored; never commit the key. **If a key has appeared in plaintext anywhere, rotate it.**
2. Restart the backend. The chat overlay's status pill will flip to `⌁ linked`.
3. Open `/occult` and click the magenta sigil bottom-right (or `Ctrl + \``). Open `/round` and tap the golden eye.

Endpoints:
- `POST /api/venice/ask` — `{ prompt, system?, model?, temperature?, max_tokens?, history? }` → `{ reply, model }`
- `GET  /api/venice/health` — `{ ready, model }`

The bridge is OpenAI-compatible. To swap Venice for your own Hugging Face inference endpoint (abliterated model, self-hosted, etc.) later, set:
```
VENICE_BASE_URL=https://your-endpoint/api/v1
VENICE_MODEL=your-model-id
```
No code changes required.

[ DISTRIBUTE OR DIE ]
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
