# Glossary

| Term | Meaning in this project |
| --- | --- |
| Especcy | Repository/project name |
| Speccy micro | Name used by the current CAD assembly and packaging study |
| Active image | The 256 × 192 Spectrum picture referenced in the sources; final border treatment is undecided |
| Candidate requirement | Proposed or inferred intent awaiting confirmation; it is not approved by being documented |
| Carrier PCB | Custom printed circuit board intended to connect and support the ESP32, display, switches and power parts |
| Clearance | Separation between modeled shapes; it does not automatically include production tolerances |
| Emulation core | Software that reproduces the chosen Spectrum machine behavior; none is selected or implemented here |
| Envelope | Outer bounding dimensions of a component or assembly |
| Extracted requirement | An obligation recovered from existing sources; stakeholder approval can still be unverified |
| FreeCAD / FCStd | CAD application and its native editable document format |
| GC9107 | Controller used by the selected LCD module |
| GPIO | General-purpose input/output pin on the microcontroller |
| GLB | Binary glTF model exchange format; this project's GLB uses metres |
| LDO | Low-dropout linear voltage regulator; a package envelope is reserved, but no electrical part is selected |
| LCD | Liquid-crystal display; the selected module has 128 × 128 pixels |
| MOSI | SPI data signal from the controller to a peripheral; called DIN on the LCD |
| MX1.25 | Connector family label used by Waveshare for this module's eight-position connection |
| Nominal | Intended design value before allowed variation is applied |
| OpenCascade | Geometry kernel used by FreeCAD for native solids and STEP handling |
| Pogo pad | Exposed contact used by a spring-loaded programming fixture |
| PSRAM | Pseudo-static RAM, an additional memory device; the selected WROOM family has none listed in W3 |
| RF | Radio frequency; this stack keeps Wi-Fi and Bluetooth disabled |
| RGB565 | A 16-bit color representation with 5 red, 6 green and 5 blue bits; used for illustrative buffer calculations here |
| ROM | Read-only memory image containing software for the emulated machine; its identity and terms are undecided |
| Snapshot | Saved emulator machine state intended to start a game; supported formats are undecided |
| SPI | Serial Peripheral Interface; the intended display data bus |
| STEP | CAD exchange format used for the complete solid assembly; this export uses mm |
| STL | Triangle-mesh format used for case and plunger exports; this project interprets coordinates as mm |
| Strapping pin | Pin sampled during reset to choose a chip startup configuration |
| Tessellation | Conversion of a solid's surface into triangles for mesh exchange or presentation |
| UART | Serial transmit/receive interface used by the proposed external programmer |
| Validation | Assessment that the resulting product suits its intended use; physical and user evidence is still pending |
| Verification | Check that a stated property or requirement is met; its result is limited to the tested scope |

Requirement categories: **BR** business intent, **USR** user need, **CON** product constraint, **MEC** mechanical, **ELE** electrical/interface, **FW** firmware behavior, **DAT** data/content, **CAD** artifact, **QUA** validation obligation.
