# Carrier electrical and placement study

Revision A adds editable KiCad 10 carrier and manual-fixture schematics, exact part selections, an **unrouted** carrier, and reproducible checks. The WROOM, LCD, six control centres and existing enclosure geometry are preserved. This completes the authorized electrical study; physical acceptance and fabrication release remain open.

Open [the preview](previews/index.html) for placement views and schematic SVGs. Open `carrier.kicad_pro` or `fixture.kicad_pro` in KiCad to edit the native circuits. The fixture has a reference schematic only, with no fixture PCB or probe mechanics.

## Files and reproduction

| File | Purpose |
| --- | --- |
| [carrier.kicad_sch](carrier.kicad_sch), [carrier.kicad_pcb](carrier.kicad_pcb) | Power, reset, straps, six controls, LCD and pogo; two copper layers, no tracks or copper fills |
| [fixture.kicad_sch](fixture.kicad_sch) | Independent fixture rail, rail monitor, two gated UART directions, manual BOOT/RESET |
| [carrier BOM](carrier-bom.csv), [LCD BOM](assembly-bom.csv), [fixture BOM](fixture-bom.csv) | One row per reference with quantity, exact MPN, footprint, source and qualification notes; no supplier pricing or purchases |
| `Study.kicad_sym`, `Study.pretty`, library tables | Local symbol/footprint snapshots; custom switch, wire and pogo pads; see [NOTICE](NOTICE) |
| [carrier STEP](previews/carrier.step) | Native KiCad placement export with nominal component models; not a certified assembled enclosure |
| [reports](reports/electrical-checks.json) | Native netlists, complete ERC/DRC JSON, firmware/BOM checks, pin coordinates, fit and power findings |
| [design.py](design.py), [build.py](build.py), [check.py](check.py) | Design inputs, native generation and cross-artifact checks |

From the repository root:

```sh
python3 hardware/electronics/build.py
```

The checked tools are KiCad **10.0.6** and FreeCAD **1.1.4**. KiCad's Python needs `pcbnew` and `wx`; FreeCAD's Python needs `FreeCAD` and `Part`. The generator otherwise uses the Python standard library. Defaults point to installed macOS applications. For another installation, set `SPECCY_KICAD_SHARE`, `SPECCY_KICAD_PYTHON` and `SPECCY_FREECAD_PYTHON`; make `kicad-cli` available and install its standard 3D models. No manufacturer documents are downloaded by the build.

Rebuilding replaces native files and generated reports. Preserve repeatable changes in `design.py` or the generator; direct KiCad edits remain valid for review but are overwritten on rebuild. `python3 hardware/electronics/check.py` checks existing netlists/BOMs/reports without generating them. Native board and STEP checks run as part of the full build.

The build checks both circuits with every ERC rule enabled and no exclusions. It checks exact pins/NCs/MPNs, firmware GPIOs, BOM parity and three deliberately incorrect netlists. It reopens the board, checks pad nets, original outline, sides, thickness and pogo access, then reopens both STEP exports. DRC is saved in full: **one shell-stake/courtyard conflict**, **70 unconnected items**, **zero schematic parity issues**. The checker requires that exact known conflict and rejects additional placement violations. Its successful exit means the study is reproduced and its gate is visible; it does not mean DRC or physical acceptance passed.

Serve the preview locally if needed:

```sh
python3 -m http.server 8790 --bind 127.0.0.1
```

Open `http://127.0.0.1:8790/hardware/electronics/previews/`. Safari inspection confirmed that all four SVG previews load.

## Carrier power and reset

J1 is GCT **USB3076-30-A**, Micro-B power only. D+/D−/ID are explicitly unconnected; the shell is grounded. Use a regulated, rated dedicated power source of at least 1 A. The circuit does not enumerate or negotiate USB host current. F1 is Bourns **MF-PSMF075X-2**, a 0.75 A resettable fuse, followed by an ESD shunt and TI **TLV75733PDBVR**. The LDO input and enable share `VBUS_FUSED`; output is 3.3 V. C1/C2 are 10 µF, 10 V X5R; C3 is a local 100 nF bypass at the module supply.

D1 **CDSOD323-T05C** has 5.0 V working peak, 6.0 V minimum breakdown and 9.8 V maximum clamp at 1 A. It does **not** protect the LDO's 5.5 V recommended / 6 V absolute input limit against sustained overvoltage. Limit the prototype source to 4.75–5.00 V at the TVS; reselect or qualify protection before using a wider input range. The 5.25 V sweep in the power report is a thermal boundary case outside this TVS rating. No system ESD result is claimed.

R1/C4 give EN a 10 kΩ pull-up and 1 µF capacitor. R2 pulls GPIO0/BOOT high; R3 and R4 hold GPIO2 and GPIO12 low. The latter preserves the module's 3.3 V flash selection. Other unused and flash-connected pins have explicit NC markers. Module ground pins 1/15/38/39 are on GND. The module footprint retains its ground-pad array with provisional 0.30 mm drills; its antenna keepout stays in DRC. Radios remain disabled.

## LCD and controls

J2 is a carrier wire-pad array, not a purchased connector. Its order matches the manufacturer's module schematic:

| Carrier pad | LCD signal | WROOM GPIO |
| --- | --- | --- |
| 1 | VCC / 3.3 V | Supply |
| 2 | GND | Ground |
| 3 | DIN | 23 |
| 4 | CLK | 18 |
| 5 | CS | 21 |
| 6 | DC | 22 |
| 7 | RST | 19 |
| 8 | BL | 25 |

Waveshare **26117** remains the selected GC9107 128 × 128 module. The manufacturer circuit has a backlight transistor; BL drives its base through 1 kΩ rather than supplying LED current directly. The module also includes its own regulator. Supply it with the specified 3.3 V. Its FAQ states up to 60 mA. Confirm the purchased revision's physical pad order after MX1.25 removal; source connector numbering alone does not prove solder-pad orientation.

SW1–SW6 are TE **2337228-2**, also named **USLPT3026EL2TR**: Up 26, Down 27, Left 32, Right 33, Fire 13, Menu 14. Each is active low to GND, using firmware pull-ups and 10 ms debounce. On the TE drawing, T1/T2 share one contact and T3/T4 share the other. The footprint numbers each pair 1 and 2 and keeps the central 1.60 × 2.60 mm free of pads, tracks, vias and fills.

## Programming contacts and fixture

Both placement views put USB at the bottom. In the **underside view**, pad 1 is leftmost. In the **front projection**, pad 1 is at CAD X = 15.75 and the numbering runs toward decreasing X. Do not copy the old generic CAD label's order. A probe carrier viewed from its contact tips must mirror the underside view; wire by number and continuity-test the mating pair.

| Pad | Device signal | Fixture connection |
| --- | --- | --- |
| 1 | GND | Common ground |
| 2 | 3V3_SENSE | High-impedance voltage sensing only; never a power input |
| 3 | UART_TX / GPIO1 | Buffer input → adapter RX |
| 4 | UART_RX / GPIO3 | Buffer output ← adapter TX |
| 5 | EN | Manual RESET switch to ground |
| 6 | BOOT / GPIO0 | Manual BOOT switch to ground |

J3 pad centres are 1.50 mm apart at CAD Y = **8.25**. This is 0.20 mm forward of the old generic pads and stays within the unchanged opening. Pads are 1.05 × 1.50 mm with no paste. Exact probes, contact force, alignment and mating sequence remain a physical gate.

The handheld receives power through Micro-B. Fixture J2 pin 1 (adapter VCC) is **NC**. Its other pins are logical GND/TX/RX, not a universal adapter cable pinout. Fixture J3 accepts its **own regulated 3.3 V ±5% rail** with common ground. That rail powers the fixture circuitry only and has no connection to device pad 2. A controller's regulated rail or a separate regulated bench source can supply it; do not obtain it from the handheld sense pad. Use a 3.3 V logic UART adapter.

TI **SN74LVC2G125DCUR** buffers both UART directions. Both active-low enables have a pull-up and share the open-drain output of **TLV7041DBVR**. A 523 kΩ / 1 MΩ divider senses the handheld; **LM4040A20IDBZR** supplies a 2.048 V reference. External feedback adds hysteresis to the comparator's internal hysteresis. The nominal enable/disable points are about **3.14 / 3.08 V**; the [analysis](reports/fixture-analysis.json) records assumptions and variation. Sense-divider current is about **2.17 µA at 3.3 V**. The comparator inputs tolerate 7 V while unpowered; the buffer has `Ioff` protection. R8/R9 define buffer input levels when an adapter or device is absent.

With the device rail absent, the enable pull-up keeps both buffer outputs high impedance. Manual BOOT/RESET only sink to GND. Confirm actual output levels, leakage and ramp/brownout behavior on hardware; static topology and datasheet limits do not prove every transient sequence.

Manual sequence after circuit/continuity review:

1. With device USB off, mate the numbered contacts and connect common ground, the local fixture rail and UART. Confirm device pad 2 is not driven.
2. Apply qualified Micro-B power. Hold BOOT, pulse RESET low for at least 10 ms, release RESET, then start esptool. Keep BOOT low through reset and the manufacturer's 1 ms strap-hold interval.
3. Use esptool's `--before no_reset --after no_reset` settings; DTR/RTS have no circuit here. Use the built mode's bootloader at `0x1000`, partitions at `0x8000` and app at `0x10000`, as described in the [firmware guide](../../firmware/README.md).
4. Release BOOT after esptool connects. After a complete flash, pulse RESET with BOOT released to run. Interrupted programming or invalid content uses the same manual bootloader entry and full reflash.

Required bench cases remain: cold boot; BOOT/RESET and normal flash; USB present/absent with fixture and adapter powered/unpowered; disconnected contacts; brownout; interrupted flash; invalid-content recovery; complete return to execution. Record device 3V3, both UART directions, EN/BOOT and off-state currents.

## Fit and thermal gates

The carrier follows the native `CarrierPCB` outline, including corner reliefs and the antenna cutout. Nominal blank size stays 20.8 × 34.8 × 0.8 mm; the cut/rounded native solid's Y extent is 34.769694 mm. KiCad's board-only STEP exports a **0.71 mm dielectric core**; copper/mask layers complete the nominal 0.8 mm stack. The report aligns the core within CAD Z = 4.8–5.6. Its 0.5 mm grid containment check supplements the exact native-board outline check; it is not a tolerance certification. Selected package envelopes show no intersection with the unchanged case/LCD solids in the checked nominal model.

| Gate | Evidence and required follow-up |
| --- | --- |
| Button actuation | TE recommends a 1.00 mm pressing tip, alignment ≤0.20 mm. Existing stems are 1.80 mm. Nominal switch top Z = 6.25 leaves only 0.05 mm to the stem at 6.30; general drawing tolerance permits Z = 6.45, giving 0.15 mm preload/interference, equal to nominal travel. Trial exact switches and actuation before revising geometry. |
| USB/Down switch | GCT 1.00 mm nominal stakes protrude 0.20 mm through the nominal 0.80 mm board, potentially 0.40 mm with drawing tolerance before PCB variation. DRC retains one stake inside SW2's courtyard. Verify contact, solder, tolerances and assembly; if it fails, explicitly revisit the socket or geometry choice. |
| USB opening | Selected socket origin X = 12.35, Y = 4.25 puts its nominal mouth at Y = 0.30. Its maximum width reaches the opening edge with zero lateral margin. Cable overmold access is unmeasured. |
| LCD and wires | Rear heights, physical pads, removal/rework and wire access remain unmeasured. No connector-clearance or assembly-order claim follows from this study. |
| LDO heat | A supply-capability budget of 500 mA ESP32 + 60 mA LCD gives 0.952 W loss at 5 V. It is not measured consumption. TI's DBV reference θJA values are 100.8 °C/W on the EVM and 231.1 °C/W on its JEDEC board; neither establishes this carrier/enclosure. At 5.25 V/560 mA/25 °C, even the EVM arithmetic gives 135.1 °C versus 125 °C recommended maximum. Measure enclosure current, transients and temperature with margin before routing/release. |
| Fuse and protection | Hold current falls to 570 mA at 50 °C and 530 mA at 60 °C. Check local self-heating and sustained current. The selected 5 V TVS also limits the qualified source range; it is not overvoltage protection. |
| Remaining qualification | Verify passive DC-bias capacitance, actual package tolerances, stock/ordering codes, probe mechanics, fabrication process and fasteners. The 10 µF Murata sheet permits ±0.15 mm in length/width/height; maxima are used here. Other passive envelopes use family allowances pending selected-part qualification. |

If the selected LDO cannot meet thermal limits, return that result for an explicit power-strategy decision. Do not treat its 1 A electrical rating, thermal shutdown or a nominal box fit as continuous-load acceptance. No enclosure, legacy CAD exports, firmware, game content, routed PCB or fabrication package is changed by this phase.

Sources and document hashes are in [sources.json](reports/sources.json), with the cross-project references in [research](../../docs/research.md). Full manufacturer PDFs remain outside the repository.
