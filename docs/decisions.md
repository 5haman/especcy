# Decision register

No accountable product acceptance owner was supplied. U2 authorizes firmware choices; U3 authorizes the electrical study; U4 resolves repository licensing for publication. All three are recorded below. Remaining decisions retain **owner not supplied**; implementation evidence does not assign a person, deadline or product approval.

## Recorded design choices

These are retrospective records of the source baseline, not newly approved architecture decisions.

| Record | Existing choice | Source | Consequence |
| --- | --- | --- | --- |
| ADR-001 | Use ESP32-WROOM-32E-N4 on a custom carrier | L1 lines 3–6, 31–32; L2 lines 5–6 | Preserve the module and the custom PCB constraint; no DevKitC substitution |
| ADR-002 | Target 24 × 38 × 12 mm including caps | L1 lines 3, 29; L3 line 274 | Nominal digital size; cable excluded; measured fit unresolved |
| ADR-003 | Use Waveshare SKU 26117 with its connector removed | L1 lines 33–38; L2 lines 7, 27 | Eight-wire assembly, measured-depth dependency, reduced display detail |
| ADR-004 | Use USB power and external UART programming | L1 lines 40–42, 56; L2 lines 17, 30 | Micro-B supplies power; an external programming fixture is required |
| ADR-005 | Disable radios and omit battery, SD, speaker and full keyboard | L1 lines 53–59; L2 lines 31–34 | Preserve the current feature and packaging boundary |
| ADR-006 | Generate Blender geometry from FreeCAD tessellation | L1 lines 72–74; L3/L4 | Native solids are the geometry origin; render details are presentation additions |

## Original decision questions

The IDs are retained from the baseline. The next section records the decisions now resolved for the firmware phase. Questions outside that scope remain open.

| ID | Question to resolve | Affected requirements | Evidence needed before resolution |
| --- | --- | --- | --- |
| D-001 | Who owns product scope and accepts business, user and technical requirements? | All; BR-001, BR-002 | Named accountable roles and recorded acceptance scope; no personal name required if a role is established |
| D-002 | Which exact switches, Micro-B socket, regulator, passives and screws replace the package estimates? | MEC-005, ELE-001, QUA-001 | Part numbers, datasheets, footprints, availability and an electrical load budget |
| D-003 | What are the purchased LCD's stack depths, active-area offset and final dimensions after modification? | MEC-003, MEC-006, MEC-007, QUA-001 | Measured sample revision and connector-removal result |
| D-004 | Which Spectrum machine model, games and compatibility behaviors define the prototype? | BR-001, USR-001, USR-002, FW-001, FW-002, FW-004 | Explicit workload and required behavior; do not infer 48K support from the render label |
| D-005 | Which emulator core, framework and toolchain versions will be evaluated and selected? | FW-001–FW-004, DAT-001 | WROOM resource measurements, interface effort and dependency/license review; W7 is only a candidate |
| D-006 | Which game input mappings, menu actions and button-combination rules are required? | USR-001, FW-002, FW-003 | Interaction definitions for the selected workload, including held and simultaneous controls |
| D-007 | How does the fixture power or sense 3V3, control EN/BOOT and avoid conflicts with USB power? | USR-003, ELE-002, ELE-004 | Schematic, pad orientation, logic levels and reset sequence; distinguish device TX/RX from adapter TX/RX |
| D-008 | How are the active image, Spectrum border, scaling filter and spare LCD rows presented? | USR-002, FW-001 | Agreed display examples with readability assessment; active 128 × 96 target remains fixed |
| D-009 | Which ROM/snapshot formats, boot flow and content replacement or persistence behavior are required? | FW-004, DAT-001 | Content model and intended update journey; no filesystem, OTA or save-state feature assumed |
| D-010 | What performance, thermal, reliability, usability and accessibility outcomes define acceptable use? | BR-001, USR-001, USR-002, QUA-002, QUA-003 | Chosen workload, environment, user assessment and justified pass limits; no arbitrary frame-rate or duration target |
| D-011 | Which case material, fabrication process, fastener specification and retention process are intended? | MEC-001, MEC-005, MEC-006, QUA-002 | Process capability and samples; modeled screw threads and gasket compression are not proven |
| D-012 | What reuse and distribution terms apply to the selected core, ROM and game content? | DAT-002 | Sources, exact dependency licenses and content permissions; no default bundling entitlement |
| D-013 | What license applies to this repository's original CAD, scripts and documentation? | CAD deliverables, DAT-002 | Explicit project-owner licensing decision; no license was present at baseline |
| D-014 | What measured tolerances are acceptable around the nominal size target and mechanical fits? | CON-002, MEC-001, QUA-001, QUA-002 | Capability of the selected parts and fabrication process; nominal CAD clearance is not a tolerance budget |
| D-015 | What happens after invalid content, interrupted programming, brownout or loss of power? | FW-005, DAT-001; quality coverage | Defined observable outcomes and recovery steps; selected architecture and content-update policy |

Decisions can be resolved independently where dependencies allow. Missing answers do not block maintenance of the current CAD documentation.

## U2 firmware resolutions — 2026-10-03

The user authorized these choices through the accepted plan and implementation request. The acceptance owner for the wider product remains D-001. Evidence is in L9 and the [verification record](verification.md).

| ID | Selected outcome for this phase | Remaining boundary |
| --- | --- | --- |
| D-004 | Spectrum 48K only; original Dizzy / Dizzy: The Ultimate Cartoon Adventure (1987), replacing Jetpack | No other game, 128K, floating-bus or raster-effect compatibility claim |
| D-005 | C++14; ESP-IDF v5.4.4; standalone `jsanchezv/z80cpp` at `2b276f0e471fa5b7f57926dc3aa3683a7f05adf5` | Target builds and host checks pass; WROOM runtime performance still needs hardware |
| D-006 | Active-low six-button binding; 10 ms debounce; Kempston directions/Fire; opposing directions neutral; Menu isolates inputs, Resume/Restart, full release before return | Physical switch/latency/readability assessment remains open; no general keyboard |
| D-008 | Average each 2 × 2 source block to 128 × 96; center with 16 border-colored rows above/below; RGB565 single DMA buffer | Actual LCD orientation, palette, tearing and user assessment |
| D-009 | 16 KiB ROM plus 49,179-byte 48K SNA compiled in mapped flash; restore a prepared Kempston starting state; replace by rebuild/UART reflash; no persistent progress | Z80 conversion and K selection occur offline only; fixture needs validation |
| D-010 | Pace 69,888 T-states per 19,968 µs and transfer the LCD every second tick, about 50.08/25.04 Hz | This resolves cadence only. Duration, acceptable overruns/latency, temperature and usability limits still need a bench acceptance decision |
| D-012 | GPLv3 core/integration is accepted; dependency notices and local content sources/hashes retained | D-013 is resolved under U4; ROM/game redistribution remains unresolved, so no ROM or game is distributed. Local downloads do not grant distribution rights |
| D-015 | Build rejects missing/invalid supported content; boot errors stop with UART reason and an LCD error when available; recovery is a complete UART reflash; power loss/restart restores the compiled SNA | Physical fault, interrupted-flash, cold-boot and power tests remain open |

U2 selected DEC-001 for bench GPIOs; U3 now checks that allocation in the carrier. DEC-002 uses the standard 1 MiB factory app, flash-backed content and a build-time SHA256 manifest. DEC-003 uses independent 10 ms debounce without held-menu repeat. DEC-004 uses the manufacturer GC9107 sequence, X+2/Y+3 offsets and initially 20 MHz SPI. The exact bindings are in the [firmware guide](../firmware/README.md); none releases a PCB. U3 resolves the fixture policy below, with physical validation open.

## U3 electrical resolutions — 2026-10-04

The user selected an LDO with a thermal gate, manual BOOT/RESET, supplier-neutral BOMs and a study without physical parts, then requested implementation. L10 and W12–W22 record the resulting evidence. Routing, procurement, fabrication release and enclosure changes are outside this phase.

| ID | Selected outcome | Remaining boundary |
| --- | --- | --- |
| D-002 | TLV75733PDBVR, TE 2337228-2 / USLPT3026EL2TR, GCT USB3076-30-A and exact passive/protection BOMs | Part availability, passive bias/tolerances, physical socket/switch fit and screws remain unqualified |
| D-007 | Device powered by Micro-B; pogo 3V3 sense only; independent fixture rail; both UART directions gated; manual BOOT/RESET with explicit mating views | No fixture PCB/probe mechanics; all power/flash/recovery cases need hardware |
| DEC-001 | Carrier GPIO map cross-checked against firmware, with unused/flash pins NC and GPIO0/2/12 straps | Routing and physical tests |
| DEC-005 | Power/protection, 10 kΩ/1 µF EN, decoupling, boot straps and fixture reference circuit selected | LDO/PPTC thermal gate, TVS source-range/ESD qualification and routing remain open |

The LDO's 1 A electrical rating does not establish continuous capability here. At the 560 mA supply-capability budget, 5 V yields 0.952 W loss. TI reference thermal boards do not represent this enclosure. The selected TVS has 5.0 V working peak, so the 5.25 V thermal sweep is outside its qualified input range. The switch-tip/height and USB stake findings in L10 must be resolved using samples or an explicit changed design choice; no geometry change is inferred.

## U4 publication resolutions — 2026-10-11

The owner selected these terms before public release on GitHub. L8 and the [verification record](verification.md#publication-checks--2026-10-11) hold the evidence.

| ID | Selected outcome | Remaining boundary |
| --- | --- | --- |
| D-013 | Source code and scripts use GPL-3.0 (`LICENSE`). Hardware design files under `hardware/` use CERN-OHL-S-2.0 (`LICENSE-HARDWARE`). Documentation, Markdown and images use CC BY-SA 4.0 (`LICENSE-DOCS`). Third-party notices keep their own terms | ROM/game redistribution stays unresolved under D-012, and the repository distributes none. Manufacturer documents and images are linked, not redistributed. No endorsement or trademark permission is implied |

Before the first push, the owner also approved removing the saved manufacturer outline and the duplicate CAD archive from history. `hardware/cad/scripts/package.py` now rebuilds the archive from committed files.

## Decisions to be taken during decomposition

These are implementation details needed after the relevant higher-level choices. They are separate from present requirement defects.

| ID | Later decision | Prerequisite |
| --- | --- | --- |
| DEC-001 | GPIO allocation, reserved pins, reset-state levels and button input circuit | Selected parts, D-006/D-007; WROOM pin/strap review |
| DEC-002 | Flash partition layout, image packaging, validation metadata and RAM allocation | D-004/D-005/D-009/D-015 |
| DEC-003 | Debounce method and timing, repeat handling and event sampling | D-006/D-010 plus switch samples |
| DEC-004 | GC9107 initialization, byte order, transfer clock, buffering and scaling implementation | D-005/D-008; measured display performance |
| DEC-005 | Regulator circuit, protection, reset network, decoupling and detailed PCB routing | D-002/D-007, manufacturer guidance and electrical review |
| DEC-006 | Wire gauge and length, fixture geometry, assembly sequence, inspection method and repair procedure | D-002/D-003/D-007/D-011/D-014 |

## How to record a resolution

Retain the ID. Add the selected outcome, responsible role, date, supporting evidence and affected requirement IDs. Mark superseded choices explicitly. Update architecture, tests and traceability together. Approval of one decision does not approve unrelated candidates.
