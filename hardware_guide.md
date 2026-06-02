# Hardware & Shielding Guide: Divine Signal Handheld

## 1. PCB Pruning & EMI Reduction
To minimize noise and maximize the sensitivity of sniffing modules (WiFi, LoRa, NFC), non-essential components on the Sipeed carrier board should be pruned:
- **Unused Connectors**: Desolder bulky pin headers (GPIO, UART) if they are not being used for expansions.
- **Status LEDs**: While useful, high-frequency switching for RGB LEDs can introduce minor noise. Use the software-controlled PWM with intention.
- **Trace Management**: Ensure that RF traces to external antennas (LoRa/WiFi) are as short as possible and use 50-ohm impedance matching.

## 2. RF Quarantine & Shielding
RF components should be "quarantined" to prevent interference with the main RISC-V processor and the display logic.
- **Shielding Cans**: The most effective way to shield RF components is to use soldered-down metal cans (tin-plated steel or nickel silver).
    - These cans should cover the WiFi/BLE and LoRa modules entirely.
    - Ensure the shield is soldered to a solid ground plane at multiple points around its perimeter.
- **Aluminum Enclosures**: For a handheld device, a CNC-machined or cast aluminum enclosure provides an excellent "Faraday cage" for the entire system.
    - Anodize the aluminum for a premium finish, but keep the internal mating surfaces raw (conductive) to ensure ground continuity.
    - Laser-engrave the "Divine Signal" logo and angelic iconography with intention.

## 3. Handheld Ergonomics
The goal is a "palm-perfect" form factor, similar to a Flipper Zero but with a larger touch interface:
- **Semi-Curved Back**: Use a 3D-printed or molded resin backplate with a slight ergonomic curve to fit the palm naturally.
- **Modular Expansion**: Use a "backpack" style connector (pogo pins or low-profile FPC) for LoRa and NFC modules to allow for quick swapping of "Divine Graces" (hardware options).
- **Internal Shielding**: If using a plastic enclosure, apply conductive copper tape or conductive spray to the inner surface, ensuring it is grounded.

## 4. Spiritual Intention in Design
The hardware is a vessel.
- Use laser engraving for angelic sigils from the grimoires of old, such as the *Ars Almadel* or the *Heptameron*. Focus on the sigils of the seven archangels (e.g., Michael, Gabriel, Raphael) to guide and protect the signal. Incorporate the name of Yahweh in Hebrew script (יהוה) with reverence.
- Avoid chaotic or demonic patterns; maintain clean, symmetrical, and geometric designs that reflect order and grace. The intention is to channel the "Divine Signal" through sacred geometry and angelic intercession.
