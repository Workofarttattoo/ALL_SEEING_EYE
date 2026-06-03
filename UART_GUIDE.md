# All-Seeing Eye | UART Access Guide

Since you are plugged into the **UART port** of your Lichee RISC-V board, you have direct serial console access. You should use a **Terminal Command** on your host machine to interact with the panel.

## 1. Connecting to the Serial Console

Use one of the following tools based on your host OS:

### Linux / macOS (Command Line)
Use the `screen` command (replace `ttyUSB0` with your actual device path):
```bash
# Baud rate is typically 115200 for RISC-V boards
screen /dev/ttyUSB0 115200
```
*To exit screen: Press `Ctrl+A`, then `K`, then `Y`.*

### Windows
Use **PuTTY**:
1. Connection type: **Serial**
2. Serial line: **COM[X]** (Check Device Manager)
3. Speed: **115200**

## 2. Interaction
Once connected, press **Enter**. You should see a login prompt or a shell (`#` or `$`).
- **User:** root (usually default for embedded RISC-V)
- **Password:** [Check your board documentation, often empty or 'lichee']

## 3. Deployment via UART
Once you have a shell via UART, you can proceed with the All-Seeing Eye installation:

1.  **Verify Node.js:** `node -v`
2.  **Run Deployment:** `./deploy_riscv.sh`

## 4. Transitioning to SSH (Optional)
If you prefer SSH, use the UART console to set up networking:
```bash
# Example for WiFi setup
nmtcli dev wifi connect "YOUR_SSID" password "YOUR_PASSWORD"
# Get IP address
ip addr show wlan0
```
Once the panel has an IP, you can `ssh root@<IP_ADDRESS>` from your main computer.

[ GHOST IN THE SERIAL ]

## Boot Log Analysis
If your screen is black but you are connected via UART, look for these markers during power-on:
- `[SPL] `: The secondary program loader is working.
- `OpenSBI vX.X`: The RISC-V supervisor interface is initializing.
- `Starting kernel ...`: The Linux OS is booting.

If you see these but the screen is still black, the **Display Driver** in your OS image is incorrect or the **FPC cable** is loose.
