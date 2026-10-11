# Requirements traceability

This matrix maps every catalogue ID to upstream evidence, the current implementation and a verification route. **Modeled** and **stored pass** do not mean physical or product acceptance. Sources are in [research](research.md); V-IDs are in [verification](verification.md).

| Requirement | Source | Current implementation or artifact | Verification | Remaining decision or evidence |
| --- | --- | --- | --- | --- |
| BR-001 | L1 48–59; L2 32–35; U2 | Candidate product intent; bounded Dizzy software phase | V-001 | D-001; wider stakeholder/physical acceptance |
| BR-002 | L1 1–10, 26–42, 76–80 | Study and documented limits | V-001 | D-001; stakeholder confirmation |
| USR-001 | L1 53–54; L2 8–14, 33; U2/L9 | Kempston, debounce and isolated menu; native cases pass | V-008 | Physical switches, item use and user assessment |
| USR-002 | L1 48–52; L2 32; U2/L9 | Runtime renderer; original Dizzy host frames inspected | V-007 | Actual LCD/readability and D-010 assessment |
| USR-003 | L1 42; L2 30; U3/L10 | Numbered sense-only pogo interface and manual gated fixture reference | V-006, V-017 | Probe mechanics and physical flash/recovery test |
| CON-001 | L1 3–6, 31–32; L2 5–6 | WROOM/carrier envelopes in L3/L7 | V-003 | Exact module qualification and routed carrier |
| CON-002 | L1 3, 29; L2 4; L3 274 | Native, STEP and Blender envelopes checked | V-002 | D-014; physical size tolerance |
| CON-003 | L1 33; L2 7; W1 | LCD envelope and artwork | V-003 | Purchased revision and physical sample |
| CON-004 | L1 40, 56; L2 17, 30; L10 | Power-only GCT Micro-B circuit; D+/D-/ID NC | V-005, V-017 | Source/protection, physical current/heat and socket fit |
| CON-005 | L1 57–59; L2 31; L9 | IDF components exclude Wi-Fi/BT; configuration guard and ELF checks pass | V-010 | Bench startup observation; preserve disabled radios |
| CON-006 | L1 53–59; L2 33–34 | Excluded from model inventory | V-003 | Preserve scope in electronics/firmware |
| MEC-001 | L1 29–30; L2 4 | L3 shell solids and spreadsheet | V-002, V-004 | D-011/D-014; process and local wall review |
| MEC-002 | L1 32; L2 5; L3 180–187; L10 | Unrouted 0.8 mm two-layer board preserves native reliefs/cutout | V-003, V-004, V-017 | Routing, part/tolerance validation |
| MEC-003 | L1 44–48 | Module/LCD placements in L3 | V-003, V-004 | D-003; measured stack |
| MEC-004 | L1 39, 45, 53; L2 8–14 | Six separate plunger solids/STLs | V-004, V-008 | D-002/D-010; actuation and usability |
| MEC-005 | L1 30; L3 137–148, 261–266 | Bosses and simplified screws | V-004 | D-002/D-011; actual fastening |
| MEC-006 | L1 38; L3 150–151, 239–241 | Ledges and foam ring | V-004 | D-003/D-011; retention and compression |
| MEC-007 | L1 37; L2 27 | Eight illustrative wires; connector omitted | V-003, V-004 | Sample modification and real routing |
| MEC-008 | L1 42, 45–46; L3 129–166 | Openings in shell solids | V-004, V-006 | Cable and fixture access |
| ELE-001 | L1 41; L3 224–228; U3/L10/W12/W16/W17 | TLV75733, protection/decoupling/reset circuit and exact BOM; ERC-clean | V-005, V-017 | LDO/PPTC thermal capacity, protection/source range and measured transients |
| ELE-002 | L1 42; L2 30; L3 207–208; U3/L10 | Numbered six-pad native board/netlist; sense-only 3V3 policy and mating views | V-006, V-017 | Probe qualification and physical power/flash cases |
| ELE-003 | L1 33, 37; L2 21, 27; W1/W2/W9/W15; L9/L10 | SPI GC9107 driver and carrier netlist agree on six GPIOs and eight LCD wires | V-005, V-007, V-017 | Physical pads, wiring, orientation, color and transfer tests |
| ELE-004 | USR-003/ELE-002; W4/W6/W18–W21; L10 | 10 kΩ/1 µF EN, boot straps and manual gated UART reference | V-006, V-017 | Physical reset, brownout, leakage and recovery tests |
| FW-001 | L1 48–52; L2 32; U2/L9 | Averaged/centered 128 × 96 renderer with border/attributes; native tests pass | V-007 | Physical GC9107 and readability evidence |
| FW-002 | L1 53; L2 33; U2/L9 | All five Kempston bits, held/diagonal/opposed cases tested | V-008 | Physical inputs and actual pickup/use case |
| FW-003 | L1 53; L2 33; U2/L9 | Resume/Restart, pause isolation and full-release gate tested | V-008 | Physical menu/latency checks |
| FW-004 | L1 56; L2 34; U2/L9 | SNA load and restart, offline game preparation; both target builds pass | V-009 | Physical startup and sustained Dizzy execution |
| FW-005 | DAT-001/FW-004; U2/L9 | Build/loader rejection, atomic failed load, boot error stop and UART recovery instructions | V-009 | Physical error/power/interrupted-programming recovery |
| DAT-001 | L1 56; L2 34; U2/L9 | Exact ROM/SNA symbols checked in mapped flash, within the factory app | V-009 | Physical provisioning and content replacement |
| DAT-002 | DAT-001; W8–W11; L9 | Core/manufacturer notices, hashes and local asset sources recorded | V-016 | D-012 content distribution; D-013 resolved under U4 |
| CAD-001 | L1 16; L3 29–40, 112–176, 267–276 | FCStd construction and design notes | V-011 | Native reopen passed; interactive edits untested |
| CAD-002 | L1 18–20; L3 exports; L4 scale/export | STEP, eight STLs and GLB exist | V-012 | STEP/STL checks reproducible with `check_exports.py`; GLB header only, no independent viewer import |
| CAD-003 | L1 67–70; L3 290–327 | Mechanical report and builder assertions | V-002, V-013 | Primary-collision pass reproduced on 2026-10-11; module and LCD contact exclusions remain |
| CAD-004 | L1 17, 48–51, 72–74; L4/L5 | BLEND and four previews | V-014 | Existing validator passed |
| CAD-005 | L1 72–73; L3/L4 | Manifest in mm; Blender import at 0.001 | V-012, V-014 | Source mapping and validator checked; presentation modifiers remain |
| QUA-001 | L1 76–80; L2 28–29; L10 | Exact part selections and circuit/placement evidence | V-003, V-005, V-015, V-017 | Purchased measurements, fit/protection qualification and routed PCB |
| QUA-002 | L1 78–79; L10 | Nominal geometry plus explicit switch/USB tolerance conflicts | V-004, V-006, V-008, V-015, V-017 | Physical samples and accepted tolerances |
| QUA-003 | L1 78–79; L10/W12/W16 | Reproducible LDO loss/reference temperature and fuse-derating arithmetic | V-005, V-015 | Actual carrier/enclosure temperature and D-010 acceptance |

All rows also inherit D-001's ownership and acceptance-authority gap. No duplicate obligation is created by listing a stakeholder need and its solution decomposition. For example, USR-002 describes the viewing experience; FW-001 describes the selected image size.

When requirements change, update this matrix and the corresponding scenario. Keep superseded IDs visible; do not recycle an ID for a different intent.
