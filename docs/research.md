# Research and source register

The selected module and LCD fit the recorded XY envelopes. External sources support their interface characteristics and identify integration work. They do not establish that the complete 12 mm assembly is electrically or physically feasible.

Research date: **2026-10-03**. Original local baseline: **`13053ce`**. Web pages were read through Safari MCP; source checkouts and code packages used Git/package downloads. The firmware phase adds pinned sources and local execution evidence. Pages using `latest` remain mutable.

## Local sources

| ID | Source and exact scope | Evidence type |
| --- | --- | --- |
| U1 | User request in this session: “research, develop full docs and requirements suite and save to docs/ and README.md” | Authorization for documentation; no product approval inferred |
| U2 | User requested the next phase, selected Dizzy instead of Jetpack, accepted the scoped plan and said “Implement the plan”; later requested “download from web” for local ROM/game checks | Authorization for the selected 48K firmware phase and local downloads; no procurement, manufacturing or redistribution permission inferred |
| L1 | [CAD README](../hardware/cad/README.md), lines 1–10 maturity; 26–42 components; 44–63 use and scope; 65–80 verification limits; 82–106 rebuilds | Original design narrative; its earlier “conversation” is unavailable |
| L2 | [Parameters](../hardware/cad/parameters.json), lines 4–18 nominal values; 19–23 source claims; 25–35 assumptions | Recorded selections and estimates; not an electrical design |
| L3 | [FreeCAD builder](../hardware/cad/scripts/build_freecad.py), lines 29–40 spreadsheet; 112–266 geometry; 267–276 design notes; 290–368 checks and exports | Implemented CAD behavior |
| L4 | [Blender builder](../hardware/cad/scripts/build_blender.py), lines 12–13 input/units; 35–74 artwork; 130–153 components; 243–347 views, export and saves | Presentation implementation |
| L5 | [Blender validator](../hardware/cad/scripts/validate_blender.py), lines 8–34 | Existing executable validation |
| L6 | [Mechanical checks](../hardware/cad/models/mechanical_checks.json), [export checks](../hardware/cad/models/export_checks.json), [Blender checks](../hardware/cad/models/blender_checks.json) | Stored results; provenance and limits are described in verification |
| L7 | [Mesh manifest](../hardware/cad/models/assembly_meshes.json), top-level `units`, `parameters`, `components` | 47 component meshes, names, categories and material labels |
| L8 | [CAD archive](../hardware/cad/speccy_micro_package.zip), 27 entries; [saved outline](../hardware/cad/reference/waveshare_085_outline.png) | Packaged artifacts and inherited manufacturer reference image |
| L9 | [Firmware guide](../firmware/README.md), `firmware/common/`, `main/`, `host/`, `tools/` and `tests/` | Implemented 48K runtime and bench bindings; executed software evidence is in verification |

## External sources inspected

| ID | Source | Verified information and limit |
| --- | --- | --- |
| W1 | [Waveshare product page](https://www.waveshare.com/0.85inch-lcd-module.htm), Specifications and Selection Guide | SKU 26117; GC9107; 128 × 128; 3.3 V; four-wire SPI; 19 × 22.5 mm board; 15.21 × 15.21 mm display; MX1.25 connector. No measured stack depth obtained |
| W2 | [Waveshare wiki](https://www.waveshare.com/wiki/0.85inch_LCD_Module), Parameters, Function Pin and ESP32 Hardware Connection | VCC, GND, DIN, CLK, CS, DC, RST, BL; 3.3 V supply and logic. Active area is 15.2064 mm per side, consistent with the product page's rounding. ESP32 example targets ESP32-S3-WROOM-1-N8R8 |
| W3 | [Espressif ESP32 module comparison](https://www.espressif.com/en/products/modules/esp32), Feature List | WROOM-32E/32UE family table: dual core, maximum 240 MHz, 4/8/16 MB flash variants, no listed PSRAM; WROOM-32E envelope 18 × 25.5 × 3.1 mm. The project's N4 selection comes from L2; exact ordering-code datasheet was not independently read |
| W4 | [ESP32 schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html), Power Supply, Chip Power-up and Reset Timing, Strapping Pins | Manufacturer recommends a 3.3 V single supply with output current no less than 500 mA; CHIP_PU reset behavior and boot-strapping constraints. This is reference guidance, not a measured project current budget or a selected regulator |
| W5 | [ESP32 PCB layout guide](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html), Positioning an ESP32 Module on a Base Board | Antenna placement, housing effects and recommended clearance of at least 15 mm in all directions. Radio performance requires final-product testing. Current design instead explicitly disables radios |
| W6 | [esptool boot-mode selection](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html), Select Bootloader Mode and Automatic Bootloader | GPIO0 low at reset enters the serial bootloader; GPIO2 and other straps matter. Automatic reset depends on external control circuitry. The six CAD pad labels alone do not implement it |
| W7 | [ESPectrum upstream](https://github.com/EremusOne/ESPectrum), README and displayed license metadata | Upstream reports ZX Spectrum emulation on ESP32 without PSRAM; its documented system uses VGA, PS/2 input and SD storage. GitHub identifies GPL-3.0. This is an investigation candidate, not a selected dependency or independently verified compatibility result |
| W8 | [Standalone z80cpp at the pinned commit](https://github.com/jsanchezv/z80cpp/tree/2b276f0e471fa5b7f57926dc3aa3683a7f05adf5), [local provenance](../firmware/vendor/z80cpp/UPSTREAM.md) | Selected Z80 core, derived from José Luis Sánchez's GPLv3 Z80Core. Original notices retained; one marked read-only prefix accessor added |
| W9 | [Waveshare code package](https://files.waveshare.com/wiki/0.85inch-LCD-Module/LCD_0.85_Code.zip), `ESP32/LCD_0inch85/LCD_Driver.cpp` | Verified initialization, RGB565, inversion, MADCTL `0xc8` and X+2/Y+3 offsets. Package SHA256 `726ecaea3da060fdd8b36c0035c6857c13c2c29785d7247d8af95c762fa7a2d6`; [permission notice retained](../firmware/vendor/waveshare/NOTICE). No physical display result |
| W10 | [Original Dizzy player](https://thecodemastersarchive.co.uk/playonline/player.php?core=fuse&rom=%2Fplayonline%2Froms%2Fzxspectrum%2Fcodemasters%2FDizzy%20The%20Ultimate%20Cartoon%20Adventure.z80&title=Dizzy%20The%20Ultimate%20Cartoon%20Adventure&autostart=1), [manual](https://worldofspectrum.org//pub/sinclair/games-info/d/Dizzy.txt), [ROM source at a pinned ESPectrum revision](https://github.com/EremusOne/ESPectrum/blob/2a2c3350eb2b26dd871fc1f98cbf4f6c93c41948/include/roms/romSinclair48K.h) | Downloaded original Dizzy extended 48K Z80 v3 for local validation. Manual: K starts with Kempston; Up jumps; Fire picks up/uses. Extracted active ROM bytes match original 48K ROM MD5 `4c42a2f075212361c3117015b107ff68`. Local-only assets; no redistribution entitlement |
| W11 | [ESP-IDF v5.4.4](https://github.com/espressif/esp-idf/tree/v5.4.4), Git checkout `296b6eab9445fd720e71aecab961e2d3fbca9944` | Selected toolchain; recursive checkout and installed ESP32 tools built both modes. Version checked by CMake; original ESP32 target, 4 MB flash, no PSRAM |

The [WROOM datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf) was discovered through W3 but not read in this review. The [DevKitC dimension drawing](https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf) and [LCD outline URL](https://www.waveshare.com/img/devkit/LCD/0.85inch-LCD-Module/0.85inch-LCD-Module-details-size.jpg) are inherited L1/L2 references, not newly verified web sources. The DevKitC outline remains a comparison prop.

## Findings and implications

| Finding | Consequence for this project | Follow-up |
| --- | --- | --- |
| Display footprint and signal names agree with the CAD assumptions | Preserve the selected product and logical interface | Measure the purchased revision and connector-removal result; D-003 |
| Waveshare's example uses ESP32-S3 | Copying its GPIO map would not define a valid WROOM-32E design | Allocate WROOM GPIOs from its own pin and strap constraints; DEC-001 |
| Module comparison lists no PSRAM for WROOM-32E | Memory feasibility cannot assume external PSRAM | Measure the chosen emulator, display buffers and stack use; D-004, D-005 |
| Upstream ESPectrum reports an ESP32 emulator | Existing work makes core evaluation worthwhile | Assess display/input/storage coupling and license obligations before selection; D-005, D-012 |
| Power supply and reset need more than package envelopes | Regulator space alone cannot prove power integrity or boot behavior | Select parts, design a schematic and validate startup/load behavior; D-002, D-007 |
| Current radio clearance is not established | Keep the existing radios-disabled constraint | Treat wireless features as a scope change; CON-005 |
| Native models and stored geometry evidence are present | Documentation can describe a checked digital study | Do not represent it as a functioning or manufacturable device; QUA-001–QUA-003 |

## Checked calculations

These are arithmetic bounds, not runtime benchmarks or acceptance thresholds.

| Calculation | Result | Assumption |
| --- | --- | --- |
| `256 / 2` by `192 / 2` | 128 × 96 pixels | U2 selects 2 × 2 RGB averaging |
| `128 - 96` | 32 spare rows | U2 selects 16 border-colored rows above/below |
| `128 × 128 × 2` | 32,768 bytes = 32 KiB | Implemented single RGB565 DMA buffer; runtime allocation still requires hardware evidence |
| `128 × 96 × 2` | 24,576 bytes = 24 KiB | One RGB565 game-area buffer |
| `2 × 128 × 128 × 2` | 65,536 bytes = 64 KiB | Two full RGB565 buffers; double buffering not selected |
| `24 × 38 × 12 / 1000` | 10.944 cm³ | Bounding-box volume; not material volume or mass |

## Remaining research

Obtain the selected module's electrical limits; exact switch, socket, regulator and screw data; measured display depths; and any intended ROM/game distribution rights. Core licensing and software build evidence are now recorded. Electrical, thermal, human-factors and hardware performance results still need physical samples. The selected frame cadence is a target, not a measured hardware result. There is no production BOM cost, lifetime or compliance claim.
