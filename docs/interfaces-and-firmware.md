# Interfaces and firmware

The repository supplies bench firmware bindings and runtime contracts for original Dizzy on Spectrum 48K. The [electrical study](../hardware/electronics/README.md) adds carrier/fixture schematics, checked GPIOs and a numbered pogo interface. Routing and physical validation remain open. Software build commands are in the [firmware guide](../firmware/README.md).

## Interface inventory

| Interface | Established intent | Unresolved contract |
| --- | --- | --- |
| Micro-B → carrier | GCT USB3076-30-A; qualified 4.75–5.00 V power only; data/ID NC | Wider source/protection qualification, cable fit and one shell-stake conflict |
| Regulator → components | TLV75733PDBVR; 3.3 V; EN tied to input | Actual load/transients and continuous thermal capability |
| ESP32 → LCD | SPI2, mode 0, initially 20 MHz; RGB565; manufacturer initialization and X+2/Y+3 offset | Physical orientation, clock margin and wire routing |
| Controls → ESP32 | TE 2337228-2 to GND; internal pull-ups; 10 ms debounce; Kempston plus isolated menu | Plunger/tolerance fit and physical input assessment |
| External programmer → pads | 1 GND, 2 sense only, 3 device TX, 4 device RX, 5 EN, 6 BOOT; two gated UART buffers, manual switches | Probe mechanics and all power/flash/recovery bench cases |
| Flash → runtime | 16 KiB ROM and 49,179-byte 48K SNA embedded in the factory app | Content redistribution rights and physical update/recovery evidence |

## LCD logical signals

These names come from W2. They describe the LCD module, not ESP32 GPIO numbers. All supply and logic connections use the manufacturer's 3.3 V interface.

| LCD name | Direction relative to LCD | Meaning |
| --- | --- | --- |
| VCC | Supply input | Module power |
| GND | Reference | Common ground |
| DIN | Input | SPI data from controller, conventionally MOSI |
| CLK | Input | SPI clock |
| CS | Input | Display chip select |
| DC | Input | Select command or display data |
| RST | Input | Display reset |
| BL | Logic input | Through onboard 1 kΩ to an 8050 backlight transistor; W15 |

“Four-wire SPI” is the product's interface description; the complete module still has eight connections including supply and controls. It does not mean four interconnect wires in this assembly. No LCD MISO/readback connection is listed in W2.

The compact model removes the connector and substitutes wires. The source labels do not verify physical pad order after removal. Confirm that order on the actual board. D-003 covers the measured sample.

## Bench GPIO binding

| Signal | GPIO | Firmware behavior |
| --- | --- | --- |
| LCD DIN / CLK | 23 / 18 | SPI MOSI/clock; no MISO |
| LCD CS / DC / RST / BL | 21 / 22 / 19 / 25 | Active-low select, command/data, reset, backlight |
| Up / Down / Left / Right | 26 / 27 / 32 / 33 | Switch to ground; pull-up enabled |
| Fire / Menu | 13 / 14 | Switch to ground; pull-up enabled |

These pins avoid flash, UART0 and boot-strapping pins. This is a bench allocation, not a PCB release. Supply the LCD at 3.3 V with common ground. The product still needs the custom carrier; a development board is only a bench fixture outside the case.

## Programming interface

U3 defines pad numbering in the electrical study: **1 GND, 2 3V3_SENSE, 3 device TX/GPIO1, 4 device RX/GPIO3, 5 EN, 6 BOOT/GPIO0**. With USB at the bottom, pad 1 is left in the underside view and right in the front projection. The fixture's contact-tip view must mirror the underside. Continuity-check mating contacts by number; the old CAD labels alone do not establish this view.

Micro-B powers the handheld. Pad 2 is high-impedance sense only; adapter VCC is disconnected. The fixture uses independent regulated 3.3 V with common ground, a TLV7041 rail monitor and two SN74LVC2G125 buffers. Device TX goes through a buffer to adapter RX; adapter TX goes through the other to device RX. The device rail's absence disables both outputs. Manual BOOT/RESET only pull to ground. EN has 10 kΩ/1 µF; GPIO0 pulls high, GPIO2/GPIO12 low.

Hold BOOT low, pulse RESET, retain BOOT through the 1 ms strap interval, then use esptool without automatic reset. Release BOOT after connection and pulse RESET after a complete flash. Bench addresses remain bootloader `0x1000`, partitions `0x8000`, app `0x10000`. See the [electrical handoff](../hardware/electronics/README.md) for fixture supply, threshold assumptions and required USB/fixture/adapter powered and unpowered cases. Static checks do not close the flash/recovery gate.

## Runtime journeys and acceptance boundaries

| Journey | Implemented behavior | Remaining evidence |
| --- | --- | --- |
| Power applied | Initialize GPIO/LCD, validate content and restore the compiled starting snapshot | Cold boot and power integrity on hardware |
| Game shown | Average 2 × 2 pixels into centered 128 × 96; border fills remaining rows | LCD orientation/colors/readability and timing |
| Direction or Fire pressed | Kempston Right=1, Left=2, Down=4, Up=8, Fire=16; opposite directions cancel, diagonals/Fire can combine | Physical switches and game action assessment; original Dizzy uses Up to jump and Fire to pick up/use |
| Menu pressed | Pause, release game inputs; Up/Down select Resume/Restart and Fire activates; Menu also resumes | Physical debounce/latency and transition checks |
| Return from menu | Require all buttons released before game inputs resume; Restart restores the compiled SNA | Host transitions pass; repeat on hardware |
| Content invalid | Reject at build; at boot, stop with UART error and `CONTENT ERROR` when LCD is available | Fault injection and reflash through the actual fixture |
| Programming interrupted | Enter serial bootloader and reflash the complete image | D-007 circuit and physical recovery test |
| Power removed | Lose current progress; next boot restores the compiled snapshot | Physical power-cycle test |

The device has no games browser, downloadable library, save-state system or content editor. Host snapshot capture prepares the starting state only.

## Display contract

FW-001 fixes the active image size at 128 × 96. U2 selects 2 × 2 RGB averaging and 16 border-colored rows above and below. The renderer follows Spectrum bitmap addressing and INK/PAPER, BRIGHT and FLASH attributes. The original CAD artwork remains illustrative.

Native tests cover literal bitmap addresses, corner pixels, averaging, border rows and FLASH. The diagnostic supplies normal/bright patterns and indicators for the emulated input mask. Readability and physical orientation still require the actual display and user assessment under D-010.

The runtime uses one 32 KiB internal DMA framebuffer, 69,888 T-states per 19,968 µs frame and one LCD transfer every second tick. UART records overruns and core/render/SPI times. These are selected pacing targets, not achieved hardware measurements. The driver has no synchronized tear-control input; visible tearing and latency need bench assessment.

## Content contract

DAT-001's ROM and one snapshot are embedded in the application in mapped flash. Supported content is exactly 16,384 bytes of ROM plus 49,179 bytes of 48K SNA. The loader validates header fields and a RAM-backed saved PC before changing machine state. ROM writes are ignored. Build manifests record SHA256 hashes; arbitrary game identity and semantic validity are not inferred from format checks.

Use a snapshot already in play with Kempston selected. The offline host can convert extended 48K Z80 v2/v3 to SNA, press K on the original Dizzy title and capture a prepared SNA. The device has no keyboard or Z80 parser. Replacing content requires rebuild/reflash. Assets and generated images stay in ignored local paths; DAT-002/D-012 distribution rights remain open.

## Firmware selection note

U2 selects C++14, ESP-IDF v5.4.4 and the standalone `jsanchezv/z80cpp` core pinned in `firmware/vendor/z80cpp/UPSTREAM.md`. Wi-Fi, Bluetooth and PSRAM components are excluded and enabled configuration symbols fail compilation. Host and ESP32 builds pass; no WROOM hardware performance result is claimed. Floating bus, raster effects, tape, sound and 128K behavior are outside this phase.

Sources: L1/L2/L9, U2 and W1–W11 in [research](research.md). Requirements: USR-001–USR-003, CON-004/CON-005, ELE-001–ELE-004, FW-001–FW-005, DAT-001/DAT-002.
