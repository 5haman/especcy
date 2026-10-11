# Development roadmap

U1 authorized the documentation baseline. U2 authorized Spectrum 48K firmware for original Dizzy. U3 authorized the electrical schematic and placement study with an LDO thermal gate and manual programming fixture. U4 authorized licensing and the public v1.0 release. The broader product stages below remain proposals without assigned owners, dates, budget or procurement authorization.

The current baseline includes the checked packaging study, a host-tested runtime and successful ESP32 builds. The physical gate must close using hardware evidence, not a CAD pass or host benchmark.

## Delivered phases

| Phase | Outcome | Evidence |
| --- | --- | --- |
| Firmware (U2) | 48K Dizzy firmware prepared for bench validation | Software outcome delivered; no physical readiness claim |
| Firmware core | Portable core/runtime, loader, display, controls and content tools | Three native test suites pass under ASan/UBSan; real Dizzy starts and walks/jumps; 15,000-frame host smoke check |
| Firmware target | ESP32 GPIO/GC9107 driver, pacing, logs and target builds | Diagnostic and Dizzy build on pinned IDF; content in flash; no Wi-Fi/Bluetooth/PSRAM components |
| Firmware handoff | Reproduction, evidence and bench handoff | [Firmware guide](../firmware/README.md), resolved scoped decisions and updated verification/traceability |
| Electrical study (U3) | Exact BOMs, carrier/fixture circuits, native placement, reproduction and handoff | Delivered in [hardware/electronics](../hardware/electronics/README.md). Both schematics ERC-clean with all rules enabled; firmware/BOM/netlist and board parity pass; native STEP reopens; previews inspected |
| Prospectus | Eight-page visual introduction | [Product prospectus](prospectus/README.md); concept visuals are labelled |
| Publication (U4) | Licenses, history purge, reproducible CAD package and export checks, CI, portfolio README and public v1.0 release | [Publication checks](verification.md#publication-checks--2026-10-11); D-013 resolved; F-003 closed |

## Open gate: hardware bench validation

| Scope | Evidence still needed |
| --- | --- |
| WROOM, LCD and Dizzy on a bench | LCD/input/action tests, cadence and heap logs, power/heat, cold boot and interrupted-programming recovery |
| Electrical design findings | LDO/PPTC heat, protection/source range, switch-tip/height, USB stake/opening, LCD modification, probe reach and power/flash/recovery tests |

The gate depends on the prepared firmware and electrical study. It does not authorize part purchases, a carrier release or enclosure changes.

The board is unrouted. DRC records one USB shell-stake/Down-switch courtyard conflict and 70 expected unconnected items, with zero schematic parity issues. No conflict is excluded. Exact part selections and conservative fit calculations do not qualify purchased parts. Preserve the enclosure and controls until a measured result supports an explicit changed choice.

## Broader product stages

| Stage | Intended outcome | Entry dependency | Evidence for an exit decision |
| --- | --- | --- | --- |
| M0 — Documentation baseline | Shared view of the current study, requirements and gaps | Existing repository and U1 | Linked suite, reviewed sources, stable IDs and relevant checks; product sign-off remains D-001 |
| M1 — Product definition | A bounded prototype workload and accountable acceptance process | Product decision owner | D-001/D-004/D-006/D-008/D-009/D-010 resolved to the detail needed for evaluation |
| M2 — Part and firmware feasibility | Evidence that selected parts and candidate software suit the intended prototype | Existing hardware constraints; workload for firmware evaluation | Measured LCD/parts; evaluated core on WROOM; display/control proof; memory, timing, power and license findings |
| M3 — Electrical and mechanical prototype design | Reviewed carrier circuit/routing and measured-part enclosure | M2 evidence, programmer policy and fabrication choices | Schematic/netlist, PCB review, actual footprints, tolerance budget and updated CAD checks; no production approval inferred |
| M4 — Integrated prototype | A device that can be programmed, display the selected game and accept controls | M3 design and working firmware/content path | V-003–V-010 and V-015 results, including failure/recovery cases and unresolved faults |
| M5 — Release decision | An explicit decision about distributing the design, software or a physical product | Prototype evidence and intended distribution scope | Accepted requirements, recorded limits, reproducible artifacts, repository/content terms and a release decision |

Part measurement can begin before the entire firmware scope is resolved. Firmware feasibility can use a suitable development setup, but passing on different hardware does not establish fit or performance in the selected compact module and case.

## Candidate work packages

| Work package | Dependencies | Requirement groups |
| --- | --- | --- |
| Confirm decision authority and prototype compatibility set | D-001/D-004 | BR, USR, FW |
| Qualify the LCD modification and exact mechanical/electrical parts | D-002/D-003 | MEC, ELE, QUA |
| Evaluate emulator/core integration without changing selected module | D-004/D-005/D-012 | FW, DAT, CON-001/003/005 |
| Define input/menu and display examples | D-006/D-008/D-010 | USR, FW-001–FW-003 |
| Design power, boot/reset and the programming fixture | D-002/D-007 and DEC-001/DEC-005 | CON-004, ELE, USR-003 |
| Route the carrier and revalidate the measured stack | Qualified parts and electrical design | MEC, QUA-001 |
| Validate physical assembly, operation and recovery | Integrated prototype and selected criteria | QUA, V-004–V-010/V-015 |

The remaining product proposals are not delivery commitments.

## Replanning rule

If the size target conflicts with measured parts or accepted usability, record the conflict and return it to the decision owner. Do not silently change the module, LCD, controls, interfaces or dimensions. Keep rejected alternatives and the evidence for a changed choice visible in the decision register.
