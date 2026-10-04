# Risk register

The principal uncertainty is whether the selected components can become a working, usable device within the modeled envelope. Geometry checks reduce one part of that uncertainty. They do not measure electrical, thermal or user outcomes.

The register uses no numerical likelihood or severity scores because the project has no supplied scoring method or sample data. Owners are not supplied. Actions below are proposed evidence-gathering work, not assigned commitments.

| ID | Risk and source | Consequence | Evidence that would reduce the risk | Related items |
| --- | --- | --- | --- | --- |
| R-001 | LCD depths, rear protrusions and active-area offset are estimated; L2 line 28 | Display, roof, carrier or window fit changes after parts arrive | Measure actual revision before committing PCB/case geometry; trial modified display stack | MEC-003/006/007; D-003; V-003/V-004 |
| R-002 | Selected switch/socket dimensions expose fit gates; L10/W13/W14 | 1.80 mm stem exceeds recommended 1.00 mm tip; height tolerance can preload 0.15 mm; USB stake enters Down switch courtyard and opening has zero lateral margin | Trial exact parts and tolerances; keep DRC conflict visible; obtain an explicit changed choice if needed | D-002/D-011/D-014; QUA-001/002; V-003/V-015 |
| R-003 | LDO thermal capacity and protection are unqualified; L10/W12/W16/W17 | 560 mA budget dissipates 0.952 W at 5 V; fuse hold falls to 530 mA at 60 °C; selected TVS working peak is 5 V and cannot clamp to LDO limits | Measure current/transients/enclosure temperature and fuse behavior; qualify source/protection; revisit LDO strategy if the thermal gate fails | ELE-001/004; QUA-003; V-005 |
| R-004 | Sense-only/manual fixture circuit is static evidence; L10/W18–W20 | Probe misalignment, power ramp/leakage or reset timing prevents safe flashing/recovery | Continuity and mating checks; device/fixture/adapter powered/unpowered, brownout and interrupted-flash tests | D-007; USR-003; V-006 |
| R-005 | Dizzy/core are selected and target static sizes measured, but WROOM execution, SPI and runtime heap are unmeasured; L9 | Firmware fails resource or responsiveness needs | Record real core/render/SPI/heap logs on WROOM; software checks and host speed cannot close the physical gate | D-010; FW-001–FW-004; `op-se7.2` |
| R-006 | The reduced display and closely spaced buttons limit detail and input; L1 lines 48–54 | Chosen games are unreadable or difficult to control | Representative game and user trials with the physical display/layout; agree acceptance method | USR-001/002; D-006/D-008/D-010 |
| R-007 | Wires, screws, button motion and fabrication variations are not covered by static collision checks; L3/L6 | Assembly interference, poor retention or stuck controls despite a geometry pass | Physical samples, tolerance analysis, assembly/rework trial and motion checks | QUA-002; D-011/D-014; V-015 |
| R-008 | Parameters, script constants, spreadsheet values and render labels overlap; L2–L4 | A change updates metadata but leaves geometry, checks or labels stale | Review coupled placements and labels; rebuild affected outputs and compare dimensions | CAD-001–CAD-005; development guide |
| R-009 | The compact stack does not establish radio clearance; L1 lines 57–59 and W5 | A later firmware change enables an unsupported wireless feature | Keep CON-005 in firmware review and runtime checks; require a new design decision for radio use | CON-005; V-010 |
| R-010 | GPLv3 core/integration and manufacturer notices are recorded; original CAD/docs license and content distribution remain open | Chosen distribution plan conflicts with applicable terms | Keep ROM/game assets private; resolve intended distribution rights and D-013 before release | DAT-002; D-012/D-013; V-016 |
| R-011 | Content rejection/reflash policy is implemented, but physical interrupted-flash and power recovery are untested | A prototype becomes unusable through the actual fixture | Exercise content errors, bootloader entry, full reflash and power cycles on hardware | V-006/V-009; `op-se7.2` |
| R-012 | Export-check and ZIP generation steps are not tracked; F-003 | Reports or downloadable package lag behind changed models | Record manual checks and archive comparison; add automation only as separately authorized implementation work | CAD-002/CAD-003; V-012 |

## Decision order

Measured parts and a selected emulator workload can be investigated in parallel as activities, without committing a board layout. Physical dimensions affect the carrier and case. Core/workload choices affect power, memory and interaction requirements. Resolve those dependencies before calling a routed board and enclosure a validated prototype.

No delivery date, procurement action or risk acceptance is granted by this register. The [proposed roadmap](roadmap.md) groups the evidence needed for later stages.
