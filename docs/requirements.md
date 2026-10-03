# Requirements catalogue

This catalogue contains **38 requirements** extracted or inferred from the [source register](research.md). It preserves the compact hardware choices. U2 separately authorizes the bounded 48K Dizzy firmware phase; catalogue status remains provenance, not approval of the entire product. No component substitution or manufacturing readiness is claimed.

## How to read the catalogue

- **E — Extracted:** stated in the repository, including its assumptions. Approval by an accountable stakeholder remains unverified.
- **C — Candidate:** inferred intent or a research-based proposal. Confirmation is required before treating it as a delivery obligation.
- **Level:** business, stakeholder or solution. A section states the level inherited by its rows.
- **Verification:** V-IDs refer to [verification scenarios](verification.md). A scenario is a way to assess the statement, not a claim that it passed.

“Shall” expresses the normalized obligation within its stated status and scope. It does not change a candidate into an approved requirement. Numeric dimensions are nominal CAD targets unless the source says otherwise. Manufacturing tolerances and operational limits are pending.

**Ownership for all rows: owner not supplied.** No sponsor, user representative or technical acceptance authority is inferred from commit authorship. D-001 tracks this gap. Implementation status and source-to-test links are in [traceability](traceability.md).

U2 selects the firmware scope under D-004/D-005/D-006/D-008/D-009 and the supported-content failure behavior under D-015. FW-004/FW-005 are implemented within that phase while their original C status remains visible. Wider business, hardware and physical acceptance decisions remain open.

## Business intent

Level: **business**. Both statements are inferred purposes rather than a supplied business case. Assess them through an agreed demonstration or study review; do not impose firmware timings on them.

| ID | Status | Requirement | Source and rationale | Assessment |
| --- | --- | --- | --- | --- |
| BR-001 | C | The project shall explore a compact handheld experience for playing ZX Spectrum games with the selected small display and six controls. | L1 lines 48–59; L2 lines 32–35. Inferred purpose of the packaging choices | V-001; D-004, D-006 |
| BR-002 | C | The packaging study shall make its size target, component assumptions and validation limits available for a decision about further prototyping. | L1 lines 1–10, 26–42 and 76–80. Inferred decision value of the study | V-001; D-001 |

## User needs

Level: **stakeholder**. The actor labels describe the documented activity; they do not assign a project role or access right.

| ID | Status | Requirement | Source | Assessment |
| --- | --- | --- | --- | --- |
| USR-001 | E | A person playing a supported game shall have four directional controls, an action control and a menu control. | L1 lines 53–54; L2 lines 8–14, 33 | V-008; U2 selects mappings; physical/user acceptance remains open |
| USR-002 | E | A person playing a supported game shall be able to view its reduced Spectrum picture on the built-in display. | L1 lines 48–52; L2 line 32 | V-007; U2 resolves D-008; perceptual acceptance remains D-010 |
| USR-003 | E | A person programming the device shall be able to use an external USB-UART adapter through the underside programming contacts. | L1 line 42; L2 line 30 | V-006; fixture and power policy await D-007 |

## Product constraints

Level: **solution / constraint**. These are selected design constraints, not open alternatives.

| ID | Status | Requirement | Source | Verification |
| --- | --- | --- | --- | --- |
| CON-001 | E | The compact assembly shall use ESP32-WROOM-32E-N4 on a custom carrier PCB; it shall exclude the full DevKitC development board. | L1 lines 3–6, 31–32; L2 lines 5–6 | V-003 |
| CON-002 | E | The modeled assembly shall have a 24 × 38 × 12 mm envelope, including button caps and excluding the USB cable. | L1 lines 3, 29; L2 line 4; L3 line 274 | V-002; physical tolerances await D-014 |
| CON-003 | E | The assembly shall use the Waveshare 0.85-inch LCD Module, SKU 26117, with GC9107 and 128 × 128 pixels. | L1 line 33; L2 line 7; corroborated by W1 | V-003 |
| CON-004 | E | The device shall receive power through a Micro-B 5 V input; that socket shall serve power only. | L1 lines 40, 56; L2 lines 17, 30 | V-005 |
| CON-005 | E | Wi-Fi and Bluetooth shall remain disabled in this display stack. | L1 lines 57–59; L2 line 31 | V-010; configuration, component and ELF checks pass |
| CON-006 | E | This compact variant shall exclude a battery, SD card, speaker, their circuits and a full Spectrum keyboard. | L1 lines 53–59; L2 lines 33–34 | V-003 |

## Mechanical requirements

Level: **solution / mechanical**. Requirements describe the nominal model or an explicitly stated assembly assumption. They do not establish fit of purchased parts.

| ID | Status | Requirement | Source | Verification |
| --- | --- | --- | --- | --- |
| MEC-001 | E | The shell shall comprise two halves with a nominal 24 × 38 × 11.6 mm outer envelope and a 1.2 mm nominal wall/roof design value. | L1 lines 29–30; L2 line 4. Local geometry varies; see hardware notes | V-002, V-004 |
| MEC-002 | E | The carrier shall use a nominal 20.8 × 34.8 × 0.8 mm envelope with corner reliefs and an antenna cutout. | L1 line 32; L2 line 5; L3 lines 180–187 | V-003, V-004 |
| MEC-003 | E | The ESP32 shall mount beneath the carrier with its shield toward the rear case; the LCD shall sit above the carrier with its 19 mm board edge across the case. | L1 lines 44–48 | V-003, V-004 |
| MEC-004 | E | The front shell shall capture six separate plungers for Up, Down, Left, Right, Fire and Menu. | L1 lines 39, 45, 53; L2 lines 8–14; L3 lines 212–222 | V-004, V-008 |
| MEC-005 | E | Two M1.4 screws shall join the case halves. | L1 line 30; L3 lines 137–148, 261–266. Purchased screw details remain estimates | V-004; D-002, D-011 |
| MEC-006 | E | The LCD shall be retained by side ledges and a nominal 0.3 mm adhesive foam gasket. | L1 line 38; L3 lines 150–151, 239–241 | V-004; D-003, D-011 |
| MEC-007 | E | The compact LCD installation shall replace the MX1.25 connector with eight short soldered wires. | L1 line 37; L2 line 27 | V-003, V-004; actual routing is unverified |
| MEC-008 | E | The case shall provide openings for the power socket, LCD, six plungers and underside programming access. | L1 lines 42, 45–46; L3 lines 129–135, 162–166 | V-004, V-006 |

## Electrical and interface requirements

Level: **solution / electrical**. The model provides envelopes and labels. It provides no netlist, PCB routing or proven circuit.

| ID | Status | Requirement | Source | Verification |
| --- | --- | --- | --- | --- |
| ELE-001 | E | The carrier design shall provide a 3.3 V supply using the reserved regulator and supporting power components. | L1 line 41; L2 line 29; L3 lines 224–228 | V-005; exact circuit and current budget await D-002 |
| ELE-002 | E | The underside programming interface shall expose GND, 3V3, TX, RX, EN and BOOT for the external UART programmer. | L1 line 42; L2 line 30; L3 lines 207–208 | V-006; pad labels do not assign actual nets |
| ELE-003 | E | The selected display shall use its eight connections: VCC, GND, DIN, CLK, CS, DC, RST and BL, with 3.3 V supply and logic. | L1 lines 33, 37; L2 lines 21, 27; W1, W2 resolve the named product interface | V-005, V-007; WROOM GPIO allocation awaits DEC-001 |
| ELE-004 | C | The carrier's reset and boot-strapping design shall support both program execution and entry to the ESP32 UART download mode. | Derived from USR-003 and ELE-002; W4 and W6 describe the required chip behavior | V-006; D-007, DEC-001, DEC-005 |

## Runtime behavior

Level: **solution / functional**. These statements describe intended future firmware; none is implemented in this repository.

| ID | Status | Requirement | Source | Verification |
| --- | --- | --- | --- | --- |
| FW-001 | E | Firmware shall present the 256 × 192 active Spectrum image at 128 × 96 pixels on the 128 × 128 LCD. | L1 lines 48–52; L2 line 32 | V-007; U2 resolves D-008; renderer tests pass; physical display open |
| FW-002 | E | Firmware shall map the four directional controls and Fire to inputs for the supported game. | L1 line 53; L2 line 33 | V-008; U2 resolves mapping; native cases pass; physical/action test open |
| FW-003 | E | The Menu control shall give access to a device menu. | L1 line 53; L2 line 33 | V-008; U2 selects Resume/Restart and transitions; native tests pass |
| FW-004 | C | Firmware shall start the selected game state using the ROM and single snapshot held in flash. | Inferred runtime use of L1 line 56 and L2 line 34; U2 selects direct SNA startup under D-009 | V-009; host startup and target builds pass; physical boot open |
| FW-005 | C | Firmware shall expose a defined failure outcome when the selected ROM or snapshot is missing, unsupported or invalid. | Coverage proposal from DAT-001/FW-004; U2 selects D-015's rejection/stop/reflash outcome | V-009; rejection tests pass; physical recovery open |

## Data and content

Level: **solution / data**.

| ID | Status | Requirement | Source | Verification |
| --- | --- | --- | --- | --- |
| DAT-001 | E | The compact variant shall store its ROM and one game snapshot in flash. | L1 line 56; L2 line 34 | V-009; U2 resolves D-009/DEC-002; mapped-flash symbols checked |
| DAT-002 | C | Each ROM, game and reused emulator component selected for distribution shall have a recorded source and applicable reuse or distribution terms. | New traceability proposal prompted by DAT-001 and W7; no legal entitlement inferred | V-016; D-012, D-013 |

## CAD and documentation deliverables

Level: **solution / artifact**. These preserve existing deliverables and implemented checks.

| ID | Status | Requirement | Source | Verification |
| --- | --- | --- | --- | --- |
| CAD-001 | E | The FreeCAD document shall preserve editable case construction, a dimension spreadsheet, labeled components and design notes. | L1 line 16; L3 lines 29–40, 112–176, 267–276 | V-011 |
| CAD-002 | E | The delivered exchange artifacts shall include an assembly STEP and eight print STL files in millimetres, plus a GLB assembly in metres. | L1 lines 18–20; L3 lines 335–362; L4 line 13 and GLB export | V-012 |
| CAD-003 | E | The geometry build shall check native shapes for validity and positive volume, check the assembled envelope, and report primary-part collisions. | L1 lines 67–70; L3 lines 290–327. Exclusions are listed in verification | V-002, V-013 |
| CAD-004 | E | The Blender presentation shall contain assembled, exploded, size-comparison and programming-access scenes with an embedded illustrative 128 × 128 screen texture. | L1 lines 17, 48–51, 72–74; L4, L5 | V-014 |
| CAD-005 | E | Blender's component meshes shall originate from the FreeCAD tessellation, with the millimetre-to-metre conversion applied. | L1 lines 72–73; L3 lines 338–362; L4 lines 12–13, 130–153 | V-012, V-014 |

## Validation obligations

Level: **solution / quality**. These are prerequisites already stated for manufacture. Numeric pass limits require later decisions, rather than invented thresholds.

| ID | Status | Requirement | Source | Verification |
| --- | --- | --- | --- | --- |
| QUA-001 | E | Before manufacture, the design shall be checked against exact selected parts, measured LCD thickness and active-area position, and the routed PCB. | L1 lines 76–80; L2 lines 28–29 | V-003, V-005, V-015 |
| QUA-002 | E | Physical-sample validation shall check connector access, solder joints, button travel and print tolerances. | L1 lines 78–79 | V-004, V-006, V-008, V-015; limits await D-010, D-011, D-014 |
| QUA-003 | E | Physical-sample validation shall check thermal behavior. | L1 lines 78–79 | V-005, V-015; workload and acceptance limits await D-010 |

## Coverage questions outside the obligation set

Performance, reliability, accessibility/usability, content recovery, release integrity, servicing and environment limits need product-level decisions before a delivery baseline can close. See D-010 and D-015. These questions do not supply invented non-functional targets. Network accounts, cloud services and telemetry are not evidenced product needs in this offline design.
