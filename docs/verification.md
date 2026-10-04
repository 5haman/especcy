# Verification and acceptance

Digital geometry, firmware software checks and electrical static checks pass. Product acceptance remains open because there is no routed carrier or physical test record. DRC retains the recorded socket/switch conflict. These results do not establish hardware timing, LCD behavior, power or fit.

## Evidence status

**Executed** means a check ran during the 2026-10-03 documentation/firmware or 2026-10-04 electrical work. **Stored** means a prior result was inspected. **Planned** means a scenario has not run. A mixed scenario can have static evidence while physical acceptance remains open.

Scenarios below derive observable outcomes from existing requirements. Candidate requirements retain candidate scenarios. Where a behavior or threshold is undecided, the scenario names the blocking decision instead of supplying a guessed pass condition.

## Scenario catalogue

| ID | Preconditions and action | Observable result or acceptance boundary | Current evidence |
| --- | --- | --- | --- |
| V-001 | Review the study and proposed use with the accountable product representative | Record whether BR-001/BR-002 reflect the intended outcome and whether the user journeys represent the intended experience | Wider acceptance planned; D-001 open. U2 selects a bounded firmware workload and controls |
| V-002 | Open the native model; inspect the component solids and assembled bounding box | Shapes are valid with positive volume; assembly envelope is 24 × 38 × 12 mm at the builder's four-decimal comparison precision. Shell target is 24 × 38 × 11.6 mm | Executed for 47 component shapes and STEP envelope; native shape/envelope checks also exist in L3/L6 |
| V-003 | Compare BOM, parameters and CAD with exact selected parts and physical measurements | Selected module/LCD and excluded components match CON-001/003/006; measured parts and board fit the accepted stack and tolerance budget | Manufacturer XY data checked; physical part qualification planned; D-002/D-003/D-014 |
| V-004 | Inspect openings, ledges, plungers, screws and gasket; then trial assembly with the selected process | Required modeled features exist. Physical parts assemble and operate against the fit/travel/retention limits selected under D-011/D-014 | CAD source inspected; physical trial planned. Current clearances are observations, not pass limits |
| V-005 | Review the schematic and routed PCB; measure startup, display-on and chosen workload behavior | Micro-B is power-only; selected components receive their documented supplies; operation and temperatures meet the selected parts' limits and D-010 criteria | Static circuits/BOM/placement in L10 checked; routing and physical power/thermal tests planned |
| V-006 | With a reviewed fixture/pinout, access the underside pads, enter download mode, program a test image and return to execution | Programming is possible through the exposed signals without an onboard USB-UART bridge; power sources and straps follow the agreed circuit; fixture reaches the pads | Numbered sense-only/manual fixture reference checked in L10; reach, functional and recovery tests remain planned |
| V-007 | Supply the known diagnostic and original Dizzy to firmware | Active image is 128 × 96, centered, averaged and bordered as D-008; physical readability meets D-010 assessment | Native bitmap/corner/averaging/FLASH tests and game frames executed. Physical LCD/orientation/readability/timing planned |
| V-008 | Exercise all buttons, held/opposing/diagonal inputs, debounce and menu transitions | Kempston/actions match D-006; pause and release gate isolate game inputs; physical travel/latency remain assessed separately | Native input/CLI/menu tests pass; host Dizzy walk/jump/diagonal observed. Actual item use, switches and user assessment remain planned |
| V-009 | Validate/load/replace ROM and SNA; test bad content and recovery | Content stays in mapped flash; prepared SNA starts; invalid data is rejected without changing machine state; reflash restores operation | Loader/converter/capture and packaging tests pass; both target modes build; missing target assets fail configuration; ROM/SNA flash symbols checked. Physical recovery/power tests planned |
| V-010 | Inspect firmware configuration, components and symbols; observe the bench startup | Wi-Fi/Bluetooth are excluded and not initialized; PSRAM is not assumed | Both target component lists/configuration/ELFs checked; radio and PSRAM initialization symbols absent. Hardware startup observation planned |
| V-011 | Open the saved FreeCAD document; inspect spreadsheet, case history, labels and notes | Editable artifacts and required objects exist; saved final case shapes reopen valid | Native reopen executed; construction and properties inspected in source. Interactive editing was not tested |
| V-012 | Open STEP/STL/GLB; check geometry scale and compare the mesh manifest with expected components | STEP and eight STLs use mm; GLB uses m; 47 named components originate from the manifest. STEP is valid and STL surfaces are closed | STEP validity/envelope and eight STL solids executed; Blender scale/names executed; GLB header checked. No independent GLB viewer round-trip |
| V-013 | Run the FreeCAD build on a preserved working copy and inspect its mechanical report | No invalid solids or reported primary collisions; expected nominal envelope. Preserve the documented collision scope and numerical cutoff | Stored report says pass; collision computation was not rerun during this documentation-only change |
| V-014 | Reopen the BLEND with the existing validator and inspect generated preview metadata | Four named views, 128 × 128 packed texture, matching component names, expected envelope, four 1800 × 1500 previews and valid GLB v2 header | Executed successfully with Blender 5.2.2 LTS; assembled render visually inspected |
| V-015 | Gather measured parts, routed PCB review and physical assembly/electrical/thermal test records | Evidence exists for QUA-001–QUA-003; unresolved fit or operational results remain open instead of inheriting the geometry pass | Planned; no manufacturing readiness claim |
| V-016 | Review selected dependencies and distributable assets with the decision owner | Sources and applicable terms are recorded; decisions resolve repository licensing and content distribution scope | GPLv3 core/integration and manufacturer notice recorded under U2. Original CAD/docs license and ROM/game distribution remain unresolved; no distribution approval inferred |
| V-017 | Rebuild the electrical study and compare native netlists/BOMs/board/STEP with firmware and unchanged CAD | Both circuits ERC-clean without disabled rules; exact pins/parts match; native artifacts open; known fit/thermal findings remain explicit | Executed in L10; unrouted DRC retains one socket/switch conflict and 70 unconnected items; physical gate open |

## Checks executed for this documentation change

| Check | Result | Limit |
| --- | --- | --- |
| FreeCAD 1.1.4 read-only reopen | All 47 manifest component objects exist; each shape is valid and has positive volume | Did not rebuild, edit or measure physical parts |
| STEP read with FreeCAD/OpenCascade | Valid shape; bounding box 24 × 38 × 12 mm | No independent manufacturing-system import |
| STL read with FreeCAD Mesh | Eight of eight report `isSolid()` | Closed mesh does not imply printable geometry or correct process tolerances |
| Existing Blender validator | `NATIVE_BLEND_REOPEN_OK`; 47 components, four scenes, packed screen, expected envelope, four previews and GLB header | Validator writes `blender_checks.json`; resulting tracked content remained unchanged |
| CAD archive comparison | All 27 ZIP entries match their repository source bytes | Archive contains the original CAD package, not the new root docs |
| Source arithmetic | Scaling, spare rows and buffer-size calculations recomputed | Memory capacity and runtime performance were not benchmarked |

The original documentation link, ID and ambiguity-scan results are recorded in the [requirements review](requirements-review.md). The following firmware results add software evidence; electrical tests remain unavailable.

## Firmware checks executed — 2026-10-03

Builds used AppleClang 21, C++14, CMake/Ninja, Python, and ESP-IDF v5.4.4 at `296b6eab9445fd720e71aecab961e2d3fbca9944` with its installed Xtensa tools. Reproduction commands are in the [firmware guide](../firmware/README.md).

| Check | Observed result | Limit |
| --- | --- | --- |
| Native CTest with ASan/UBSan | `runtime`, `host_cli`, `snapshot_converter`: all pass; loader/capture/registers, bus/interrupt timing, pixels/FLASH, debounce/menu isolation, CLI and malformed content covered | No complete CPU conformance or general Spectrum compatibility claim |
| Diagnostic ESP32 build | Successful 4 MB ESP32 image; binary size recorded in the firmware guide; standard 1 MiB factory app has 75% free | Compiled only; no board attached |
| Dizzy ESP32 build | Successful with the locally prepared ROM/SNA; static DRAM 62,676 bytes and IRAM 55,590 bytes | Runtime heap, 32 KiB DMA allocation, stack and cadence require hardware |
| Flash content and excluded components | ROM/SNA symbol lengths 16,384/49,179 in `0x3f4…` mapped flash; `esp_wifi`, `bt`, `esp_psram` absent; corresponding initialization symbols absent | Configuration/link inspection, not RF or electrical measurement |
| Missing Dizzy assets | Target configuration fails with the required ROM/SNA path message | Fault injection on physical flash still open |
| Real game preparation | Extended 48K Z80 v3 converted offline; K held 25 frames, released; first level captured after 150 frames as a SNA | Local content identity/provenance is recorded below; assets remain ignored |
| Real game inputs | From the same prepared SNA, 25-frame Left/Right/Up/Right+Up runs visibly change position/jump relative to idle; all five Kempston bits are covered by diagnostic execution | Fire in the initial screen produces no visible item action; an appropriate pickup/use case remains in the bench gate |
| Sustained host smoke check | 15,000 frames; 1,048,320,037 T-states including carried overshoot; 299.52 emulated seconds; no sanitizer errors | Host ran without real-time pacing; this is not a WROOM speed/stability measurement |

The downloaded Z80 is 44,114 bytes, SHA256 `4f1b4fa53ac2ac8506976fc687efbfa789320a5fcff9a30f414f09ce66145e25`. The original 48K ROM is 16,384 bytes, SHA256 `d55daa439b673b0e3f5897f99ac37ecb45f974d1862b4dadb85dec34af99cb42`, MD5 `4c42a2f075212361c3117015b107ff68`. Sources are W10. Local `private/download-sources.json` and build `content/content.json` retain provenance and generated hashes. They are not distributed assets.

Beads `op-se7.2` retains the physical gate: diagnostic/Dizzy LCD and switch checks, about 50.08 Hz emulation/25.04 Hz LCD, UART core/render/SPI/heap evidence, actual item use, power/thermal behavior and programming recovery. Do not close it using these software results.

## Electrical checks executed — 2026-10-04

L10's single build command uses KiCad 10.0.6, its `pcbnew` backend and FreeCAD 1.1.4. The [electrical handoff](../hardware/electronics/README.md) gives exact reproduction, source hashes and qualification boundaries.

| Check | Result | Limit |
| --- | --- | --- |
| Carrier and fixture ERC | Zero violations; all rules enabled; no exclusions | Static electrical consistency, not circuit simulation or bench evidence |
| Native XML / exact BOMs / firmware | Every declared pin/NC/MPN and BOM row matches; six inputs and six LCD GPIOs cross-checked; three intentional miswires rejected | GPIO topology only; no physical connector-order or waveform proof |
| Native board reopen | 21 footprints, two copper layers, 0.8 mm nominal thickness, exact pad nets/outline, no tracks; pogo stays within the original opening | Unrouted study |
| Native DRC and schematic parity | Zero schematic parity issues; one USB shell-stake/SW2 courtyard conflict; 70 unconnected items; full report retained | DRC does not pass; no manufacturing release |
| STEP and unchanged native CAD | Both STEP files valid; 20 solids in component export; original outline matches; dielectric core and selected envelopes inspected | No nominal case/LCD body intersections found; socket stake, switch tip/height, wire routes and tolerance gates remain open |
| Power and fixture arithmetic | 0.952 W LDO loss at 5 V/560 mA; fuse derating recorded; nominal UART-enable thresholds 3.14/3.08 V; sense divider 2.17 µA | Reference thermal boards and comparator allowances do not establish real temperature, current or every transient/power-off case |
| Safari preview inspection | Four SVGs load; carrier/fixture diagrams and mirrored placement views inspected | Preview only; no physical device |

V-017 adds the repeatable static handoff: both circuits pass ERC without disabled rules, exported pins/BOM/firmware agree, native board/STEP open, and expected unrouted connections and exact unresolved fit findings remain visible. V-003/V-005/V-006/V-015 and `op-se7.2` stay open until samples, routing and physical electrical/thermal evidence exist.

## Collision-check scope

L3 validates every component's shape and volume. For pairwise collisions it selects categories `hardware` and `case`: **30 components** in the current manifest. Fifteen `detail` objects and two `fastener` objects are outside that pairwise set, including illustrative wires and screw details.

The algorithm checks intersecting bounding boxes, then reports common volume above `1e-5 mm³`. It contains exclusions for ESP shield/substrate and LCD PCB/panel contacts. Its case-contact exclusion uses `CaseBase`/`CaseLid`, while the native object names are `LowerWithBosses`/`UpperFinished`; that exclusion therefore does not match those objects. The stored result still reports no collisions. A future change should not assume that case exclusion is effective.

The pass flag combines invalid-solid, reported-collision and envelope checks. The displayed `case_wall_mm`, `button_hole_radial_gap_mm` and `lcd_window_edge_gap_mm` values are assigned constants. They are not independent minimum-wall or fit measurements. The report does not check wire motion, button stroke, solder volume, thread engagement, gasket compression, electrical operation or fabrication tolerance.

## Acceptance record for future work

For each executed scenario, record requirement IDs, commit/artifact identifiers, tool or equipment version, sample/part revision, setup, input/workload, observed result and unresolved failures. Record the acceptance decision separately from the test result. An accountable role must resolve any waiver; this suite grants no waiver authority.
