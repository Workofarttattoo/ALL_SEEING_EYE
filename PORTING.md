# Porting Guide: All-Seeing Eye to RISC-V Smarthome Panel

This document outlines the hardware-specific dependencies and required adjustments for porting the PoisonTap 2026 / All-Seeing Eye project to a RISC-V based Linux smarthome panel.

## Hardware Dependencies in `pi_startup_2026.sh`

1.  **USB Gadget Controller (UDC):**
    - Path: `/sys/class/udc`
    - Dependency: Requires a USB controller with gadget support. RISC-V boards (like those from Sipeed or StarFive) may have different UDC names or require different kernel modules (e.g., `dwc2`, `musb-hdrc`).
2.  **USB Interface Name:**
    - Variable: `WLAN_IF="usb0"`
    - Dependency: The system assumes the CDC-ECM interface will be named `usb0`. This should be verified on the target RISC-V board using `ip link`.
3.  **USB ConfigFS:**
    - Path: `/sys/kernel/config/usb_gadget/`
    - Dependency: Requires `configfs` support in the kernel and the `libcomposite` module loaded.
4.  **LED Control:**
    - Path: `/sys/class/leds/led1/brightness`
    - Dependency: This is specific to the Raspberry Pi Zero 2 W ACT LED. RISC-V panels will have different LED paths (e.g., `/sys/class/leds/green/brightness`).
5.  **Hardcoded Paths:**
    - Path: `/opt/poisontap/`
    - Dependency: The script assumes the project is installed in `/opt/poisontap/`. This should be made configurable or adjusted for the target environment.

## Recommendations for RISC-V WAFT Panels

- **WAFT Support:** If the panel uses the WAFT (Web Application Framework for Things) framework, the UI should be served via an embedded browser.
- **Antennae/WiFi:** Since the user mentioned an antennae, consider using the actual wireless interface (`wlan0`) for C2 communication or as an alternative injection vector if USB gadget mode is not supported by the hardware's USB port.
- **Performance:** RISC-V cores in smarthome panels are often lower power. Async I/O and memory caching are critical.
