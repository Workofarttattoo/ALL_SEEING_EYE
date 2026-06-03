# All-Seeing Eye | OS Flashing & Boot Troubleshooting

If you have a black screen after plugging in your Lichee RISC-V board, it is likely because the **SD card is empty** or has not been flashed with a bootable Linux image.

## 1. Do I need to preprogram the SD card?
**YES.** Unlike a desktop PC, these boards do not have an OS pre-installed on the hardware. You must "flash" a specialized Linux image onto a microSD card.

## 2. Recommended OS Images
For the Lichee-powered 86 Panel, use one of the following:
- **Tina Linux (WAFT Integrated):** Best for preserving the legitimate WAFT UI style.
- **Debian/Ubuntu for Lichee:** Better for full Node.js support.
- **Download Link:** [Check LicheePi Documentation / Sipeed Wiki for the latest '.img' files]

## 3. How to Flash
1.  **Download** a tool like **balenaEtcher** or **Rufus**.
2.  **Insert** your microSD card (16GB+ recommended) into your computer.
3.  **Select** the downloaded `.img` file.
4.  **Flash!**

## 4. Why is my screen black? (Troubleshooting)
If you flashed the card and it still won't turn on:

1.  **Check UART Output (Crucial):**
    - Connect your UART cable (see `UART_GUIDE.md`).
    - If the board is alive, you will see text like `HELLO! SPL...` or `OpenSBI` on your terminal even if the screen is black.
    - If you see **nothing** on UART, your power supply is likely too weak or the board is not receiving power.
2.  **Power Supply:**
    - The Lichee 86 Panel requires **5V 2A** minimum. Using a standard computer USB port often isn't enough.
3.  **FPC Cable Seating:**
    - Ensure the ribbon cable connecting the board to the screen is fully inserted and the latch is locked.
4.  **SD Card Quality:**
    - Use a **Class 10** or **U3** high-speed card. Cheap cards often fail during the boot process.

[ THE VOID REQUIRES POWER ]
