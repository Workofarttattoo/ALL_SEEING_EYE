# Platform Comparison: Raspberry Pi 5 vs. Sipeed RISC-V (Smarthome UI Panel)

## 1. Hardware Performance
*   **RPi 5**: Quad-core ARM A76 @ 2.4GHz. Overkill for PoisonTap but excellent for heavy sniffing/decoding (e.g., SDR).
*   **Sipeed RISC-V (D1/BL808)**:
    *   **D1 (Lichee RV)**: Single-core XuanTie C906 @ 1GHz. Capable of Linux/ConfigFS.
    *   **BL808 (M1s)**: Triple-core (D0 @ 480MHz, M0 @ 320MHz, LP @ 32MHz). RISC-V 64/32 mix. Integrated WiFi/BLE/Zigbee.

## 2. USB Gadget (PoisonTap)
*   **RPi 5**: Stable support via `dwc3`.
*   **Sipeed**: The D1 (Lichee RV) supports USB OTG and ConfigFS. BL808 USB support in Linux is more experimental but usable for CDC-ECM.

## 3. Radio Support
*   **WiFi/BLE**: Integrated on most Sipeed boards. Sipeed's drivers for "Monitor Mode" (WiFi sniffing) are more restrictive than RPi's.
*   **LoRa**: Requires external SPI module (SX1276/SX1262). RPi has better SPI throughput; Sipeed is more power-efficient.
*   **NFC**: Requires I2C/SPI module (PN532). Both platforms handle this well.

## 4. Form Factor (The Handheld Goal)
*   **Sipeed Smarthome UI**: Built-in 4" or 7" panels are significantly thinner than an RPi 5 + Hat. Ideal for a "palm-sized" device.
*   **Mounting**: The Sipeed panels usually have a flat back with FPC connectors. A "semi-curved" handheld would require a custom 3D-printed or CNC frame to house the battery and modules behind the panel.

## 5. Software Stack (Waft)
*   **Waft**: Sipeed's WebAssembly UI framework. Highly efficient for RISC-V. We can port the PoisonTap C2 dashboard to Waft for local monitoring.
