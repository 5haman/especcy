# Hardware specification

The assembly is a nominal digital model. Its geometry and manufacturer XY dimensions have evidence; its unselected parts, electrical design and fabrication fits do not yet have physical evidence.

## Coordinates and dimensions

All CAD dimensions below use **millimetres**. X is the 24 mm width, Y is the 38 mm length and Z runs from the outer rear face toward the display. The USB opening is near Y = 0. These coordinates come from L2 and L3.

| Element | Nominal size or extent | Evidence and limit |
| --- | --- | --- |
| Complete assembly | 24 × 38 × 12 | Native/STEP/Blender envelope; cable excluded |
| Shell | 24 × 38 × 11.6; seam Z = 6.4; outer corner radius 3 | Design choices; exact corner and fit profiles are in native geometry |
| Wall/roof parameter | 1.2 | Nominal value, not a guaranteed local minimum. The upper cavity uses 1.1 mm XY offsets and separate relief geometry |
| Carrier | 20.8 × 34.8 × 0.8; origin (1.6, 1.6, 4.8) | Blank envelope with corner reliefs and antenna cutout; unrouted |
| ESP32 module | 18 × 25.5 × 3.1; assembly extent Z = 1.7–4.8 | WROOM envelope from W3; model divides substrate and shield |
| LCD PCB | 19 × 22.5 × 0.8; origin (2.5, 14.3, 7.3) | XY corroborated by W1/W2; board depth estimated |
| LCD front panel | 18 × 18 × 2; origin (3, 18.05, 8.1) | Estimated panel envelope |
| LCD rear components | 1.2 mm modeled height below PCB | Estimated packages; exact parts and protrusions unmeasured |
| LCD active area | 15.21 × 15.21; center (12, 27.05) | Area corroborated by W1/W2; center offset estimated |
| Window | 15.81 × 15.81 | Design value; nominal edge allowance 0.3 |
| Gasket | 0.3 mm thickness, Z = 10.1–10.4 | Retention concept; compression and adhesive unselected |
| Micro-B socket | 7.5 × 5.9 × 2.5; origin (8.25, 0.8, 2.3) | Generic package; cable overmold and plug envelope unmodeled |
| USB opening | 8.3 mm wide × 3.3 mm high | Opening geometry only; purchased connector fit pending |
| Programming opening | 10.2 × 2.8 plan envelope | Fixture reach and orientation unproven |

The native document also contains simplified contacts, wires and screw geometry. Do not derive a manufacturing footprint from those visual approximations.

## Controls

All six caps have a modeled 3.5 mm diameter. Switches use a generic 3 × 2.6 × 0.65 mm envelope. The flange and stem geometry capture each cap, but the model does not establish actuation force, stroke, return behavior or debounce.

| Control | X center | Y center |
| --- | ---: | ---: |
| Up | 7.4 | 11.5 |
| Down | 7.4 | 4.5 |
| Left | 3.9 | 8.0 |
| Right | 10.9 | 8.0 |
| Fire | 18.6 | 10.8 |
| Menu | 18.0 | 5.4 |

The reported button-hole radial gap is 0.21 mm. It is a nominal CAD gap, not a proven process tolerance. Usability of this closely spaced layout needs the assessment selected in D-010.

## Component register

This is a **model inventory**, not a purchase-ready bill of materials. Quantities for generic electronics describe rendered envelopes rather than a complete circuit.

| Item | Modeled quantity | Selection status |
| --- | ---: | --- |
| ESP32-WROOM-32E-N4 | 1 | Selected module; verify exact ordering data and purchased marking |
| Waveshare SKU 26117 | 1 | Selected module; connector modification assumed |
| Custom carrier PCB | 1 | Envelope only; no schematic, netlist, stack specification or fabrication files |
| Low-profile tactile switches | 6 | Generic; part number and stroke pending |
| Micro-B socket | 1 | Generic; power-only intent |
| 3.3 V LDO | 1 | SOT-23-5 envelope; no selected electrical part |
| Capacitors | 3 | Generic 0603 envelopes; values and required circuit quantity unresolved |
| EN/BOOT pullups | 2 | Generic 0402 envelopes; circuit values unresolved |
| Programming contacts | 6 pads | Geometry only; not an onboard USB-UART bridge |
| LCD interconnects | 8 | Illustrative wire routes; wire specification unresolved |
| Foam gasket | 1 | Material, adhesive and compressed thickness unresolved |
| Case halves and plungers | 2 halves + 6 plungers | Printable mesh artifacts; fabrication process unselected |
| M1.4 screws | 2 | Simplified geometry; length, thread engagement and sourcing pending |

No quantities or costs for manufacturing consumables, protection parts, fixtures or packaging have been estimated.

## Reported clearances

| Pair | Stored nominal clearance | Interpretation |
| --- | ---: | --- |
| ESP32 shield to case floor | 0.5 mm | No component or fabrication tolerance applied |
| Carrier to LCD PCB | 1.7 mm | Rear display components occupy part of this region |
| LCD panel to roof | 0.3 mm | Gasket occupies the planned interface |
| Regulator to display PCB | 1.055 mm | Simplified package-to-shape distance |

L6 records these results. The script computes shape distances; they are not electrical creepage limits, assembly allowances or measured thermal clearances.

## Electrical preparation

The schematic needs to define power regulation, protection, reset/boot biasing, decoupling, switch circuits, LCD control and programmer power handling. W4's supply guidance is a design input; total load must include the display and the selected operating workload. A small LDO envelope does not establish available current or heat dissipation.

Use the selected WROOM module's pin constraints. W2's ESP32-S3 example does not supply this board's pin map. Review flash-connected pins and boot straps before assigning controls. See [interfaces and firmware](interfaces-and-firmware.md).

## Proposed physical validation sequence

This is a planning sequence, not a released assembly instruction.

1. Select exact parts and measure the LCD, including its active-area location and depth after connector removal.
2. Update the stack and footprint drawings using those measurements. Resolve fabrication tolerances and fastener details.
3. Design and review the schematic and carrier routing. Check power, reset and programmer connections before energizing a prototype.
4. Validate electronics and display behavior on the chosen prototype arrangement. Record currents and temperatures for the selected workload.
5. Trial the case, plungers, gasket and wire route. Check cable overmold access, fixture reach and assembly order on a physical sample.
6. Record fit, button actuation and thermal findings against V-015 before claiming manufacturing readiness.

Sources: L1 lines 26–80; L2; L3 lines 112–266; L6; W1–W6. Related requirements: CON-001–CON-006, MEC-001–MEC-008, ELE-001–ELE-004 and QUA-001–QUA-003.
