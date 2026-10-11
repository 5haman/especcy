# Speccy micro — compact ESP32 packaging study

The modeled assembly measures **24 × 38 × 12 mm**, including the button caps.
It uses the ESP32-WROOM-32E module selected for this study on a custom
carrier PCB, with a tiny display, six buttons, and a two-part case.
It does not use the full DevKitC development board.

This is a mechanical packaging target. It is not a proven absolute minimum,
an electrically complete PCB design, or a case validated against purchased parts.

## Files

| File | Purpose |
| --- | --- |
| `models/speccy_micro.FCStd` | Editable FreeCAD document, case boolean history, dimension spreadsheet, labeled components and design notes |
| `models/speccy_micro.blend` | Blender presentation: assembled, exploded, size comparison, and rear programming access scenes |
| `models/speccy_micro_assembly.step` | Complete CAD assembly for other CAD software; millimetres |
| `models/speccy_micro.glb` | Portable assembled model with its screen texture embedded; metres |
| `meshes/case_base.stl`, `meshes/case_lid.stl` | Case mesh exports in millimetres; lid flipped with its outer face on the print bed |
| `meshes/button_*.stl` | Separate plunger meshes in millimetres |
| `renders/*.png` | Presentation views and the illustrative 128 × 128 screen texture |
| `models/mechanical_checks.json` | Native geometry checks and numerical clearances |
| `parameters.json` | Nominal dimensions, component positions, source URLs, and assumptions |
| [Manufacturer LCD outline](https://www.waveshare.com/img/devkit/LCD/0.85inch-LCD-Module/0.85inch-LCD-Module-details-size.jpg) | Linked reference drawing; not redistributed here |

## Assembly and size

| Item | Modeled envelope / role | Evidence |
| --- | --- | --- |
| Outer case | 24 × 38 × 11.6 mm; caps raise total height to 12 mm | Design choice |
| Case walls / roof | 1.2 mm nominal; two M1.4 screws join the halves | Design choice; fastener fit needs a sample |
| ESP32-WROOM-32E-N4 | 18 × 25.5 × 3.1 mm; mounted beneath the carrier | Espressif published module envelope |
| Custom carrier PCB | 20.8 × 34.8 × 0.8 mm; corner reliefs and antenna cutout | Unrouted design envelope |
| Waveshare 0.85-inch LCD, SKU 26117 | 19 × 22.5 mm board; 128 × 128 pixels; GC9107 SPI | Manufacturer footprint and specifications |
| LCD active area | 15.21 × 15.21 mm | Manufacturer specification |
| LCD depth | 0.8 mm board + 2 mm front panel; 1.2 mm rear components | Estimated; measure an actual module |
| LCD connector | MX1.25 removed; eight short wires replace it | Required modification for the 12 mm stack |
| LCD mounting | Side ledges and a 0.3 mm adhesive foam gasket | Mechanical concept |
| Six switches / caps | Generic 3 × 2.6 × 0.65 mm switches; 3.5 mm cap diameter | Package estimates; choose exact purchased parts |
| Micro-B socket | Generic 7.5 × 5.9 × 2.5 mm; mounted beneath carrier | Package estimate; 5 V input only |
| Power parts | Small 3.3 V LDO, capacitors, and EN/BOOT pullup envelopes | Space reservation; circuit not validated |
| Programming | Six underside pogo pads: GND, 3V3, TX, RX, EN, BOOT | External USB-UART adapter required |

The carrier rests on side ledges. The ESP32 shield faces the rear case; the
screen sits above the carrier. The front shell captures the six button plungers.
The USB socket occupies the space below the buttons, on the opposite PCB face.

The display is oriented with its 19 mm edge across the case. Its 128 × 128
pixels can show the original 256 × 192 Spectrum picture at **128 × 96**, a
2:1 reduction in each direction. The screen render is illustrative artwork,
not output from a working emulator. This display can serve a tiny game device;
BASIC text is difficult to read and individual Spectrum pixels are lost.
The controls provide four directions, action, and menu; a full keyboard is
outside this assembly.

USB powers the device. ROM and a game snapshot would live in flash. The model
excludes a battery, SD card, speaker, and their circuits. The dense display
stack requires **Wi-Fi and Bluetooth to remain disabled**; the antenna cutout
does not establish adequate RF clearance from the display.

The size comparison uses the **27.94 × 48.26 mm DevKitC V4 PCB footprint** at
the same scale. It is a reference outline, not a complete development-board
assembly. Its case, headers, and antenna overhang are excluded.

## Verification and limits

The build checks native solid validity, positive volume, the assembled bounding
box, and intersections between primary mechanical parts. Small visual details
and simplified screw threads are excluded from collision checks. The script
also reopens the saved FreeCAD document and verifies its case solids.

The Blender model uses meshes tessellated directly from those FreeCAD solids.
Its small edge bevels and surface labels are for presentation. The saved file
contains four named scenes and an embedded screen texture.

Before manufacture, choose exact switch, regulator, USB socket and screw part
numbers; measure the LCD thickness and active-area position; route and check
the PCB; check connector access, solder joints, button travel, thermal behavior,
and print tolerances on a physical sample. The sources establish component
envelopes, not a completed electrical implementation.

## Rebuilding

On macOS, with both applications installed in `/Applications`:

```sh
QT_QPA_PLATFORM=offscreen /Applications/FreeCAD.app/Contents/Resources/bin/python -u hardware/cad/scripts/build_freecad.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --python hardware/cad/scripts/build_blender.py
```

Run from the project root. FreeCAD is 1.1.4 and Blender is 5.2.2 LTS in the
current environment. Other installations need the FreeCAD Python library path
adjusted in the script. FreeCAD's GUI runs hidden solely to preserve view
properties; Blender renders the previews. The script exits after all saves and
assertions to avoid a macOS offscreen OpenGL teardown fault.

The case spreadsheet drives the main shell dimensions. Component locations,
openings, ledges and fasteners remain explicit design placements; changing
dimensions requires checking those placements and rerunning the build checks.
`parameters.json` records the nominal design; it is not an automatic layout
optimizer.

After rendering, check the saved Blender document with:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background hardware/cad/models/speccy_micro.blend --python hardware/cad/scripts/validate_blender.py
```

Then check the exported STEP and STL files, and build the downloadable package:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/python hardware/cad/scripts/check_exports.py
python3 hardware/cad/scripts/package.py
```

`check_exports.py` rewrites `models/export_checks.json`. `package.py` writes a
reproducible `dist/speccy_micro_package.zip` from the committed files in this
folder and the three license files. Tagged GitHub releases attach that archive.

## Sources

- [Espressif ESP32 module comparison](https://www.espressif.com/en/products/modules/esp32): module envelope and processor specifications.
- [Waveshare 0.85-inch LCD](https://www.waveshare.com/0.85inch-lcd-module.htm): board size, pixels, active area, controller and supply.
- [Waveshare mechanical outline](https://www.waveshare.com/img/devkit/LCD/0.85inch-LCD-Module/0.85inch-LCD-Module-details-size.jpg): carrier outline and mounting features.
- [Espressif DevKitC V4 dimensions](https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf): reference PCB dimensions; checked against the official drawing's indexed dimensions.
