# Product brief

Especcy contains a concept called **Speccy micro**: a very small USB-powered handheld for playing ZX Spectrum games with six controls. It now supplies a digital packaging study and 48K Dizzy bench firmware. A functioning physical device remains unverified.

## Purpose and value

The inferred purpose is to explore how a selected ESP32 module and a small display can fit into a compact game device. The design accepts reduced image detail and limited input to reach its current size target. These are candidate business intentions, BR-001 and BR-002, derived from L1 and L2 rather than a supplied business case.

No sales, cost, demand, revenue, production-volume or delivery-date target has been supplied. This brief does not infer a commercial product or an absolute size record.

## Audiences and journeys

These audience descriptions are inferred from the documented activities. They do not assign ownership or permissions.

| Audience | Intended journey | Present evidence |
| --- | --- | --- |
| Person playing a compatible game | Apply USB power, view the game, use directions and Fire, access a menu | Host runtime and ESP32 builds exist; physical display/control experience remains untested |
| Person assembling a prototype | Obtain measured parts, build the carrier, install the display and plungers, close the case | Assembly geometry exists; sourcing and process validation are pending |
| Person programming a prototype | Reach underside pads with an external UART fixture, load firmware and content | Pad geometry and firmware/build procedure exist; fixture wiring and physical recovery remain pending |
| CAD contributor | Open the native files, change the design, rebuild and inspect exports | Scripts and models exist; relevant native checks pass |

U2 selects original Dizzy on Spectrum 48K with Kempston inputs and a Resume/Restart menu. Software evidence now supports that scope. The illustrative CAD `48K` label remains separate from the runtime and physical acceptance evidence.

## Scope boundary

| In the current design | Outside the current design | Undecided |
| --- | --- | --- |
| ESP32-WROOM-32E-N4; custom double-sided carrier envelope; IDF v5.4.4 and pinned Z80 core | Full DevKitC board inside the case | Hardware runtime/fit evidence |
| 0.85-inch Waveshare LCD; eight-wire modification; original 48K Dizzy with SNA | Battery, SD card, speaker, 128K and other game claims | Physical display and wider compatibility |
| Four directions, Fire and Menu; Kempston and Resume/Restart | Full device keyboard | Switch samples, action/latency and user assessment |
| Micro-B power and external pogo programming; bench GPIO binding | USB data through the Micro-B socket | Final netlist, fixture power/reset policy |
| Wi-Fi and Bluetooth disabled | Wireless features in this compact stack | Exact electrical parts, PCB stack and thermal limits |
| Editable CAD and presentation assets | Manufacturing-ready assembly or proven minimum size | Fabrication process, yield, costs and distribution terms |

## What would demonstrate progress

The current study can be assessed by opening its editable files, checking its modeled envelope and reviewing its assumptions. Those checks do not require a working emulator.

A functioning prototype still needs measured fit, power and programming evidence, and the selected game on the actual display and six switches. Cadence is selected at about 50.08 Hz emulation/25.04 Hz LCD; achieved performance, run duration, thermal limits and user acceptance remain open. See [verification](verification.md), [decisions](decisions.md) and the [roadmap](roadmap.md).

## Constraints and tradeoffs

The 128 × 128 LCD contains a 128 × 96 image from 2 × 2 averaging of the 256 × 192 picture. The firmware uses the remaining 32 rows as 16 border-colored rows above/below. Text and individual source pixels lose detail during reduction; physical readability remains untested.

USB power supports a compact model by excluding a battery. External programming avoids reserving an onboard USB-UART bridge. Connector removal reduces the LCD stack height but adds assembly work and rework risk. Disabling radios preserves the documented scope; it does not certify the enclosure or electrical design.

## Authority and maturity

The product decision owner and technical acceptance owner were not supplied. Remaining decisions retain **owner not supplied**. U1 authorizes the documentation baseline; U2 authorizes the scoped firmware phase. Neither authorizes procurement, manufacturing or acceptance of unrelated product requirements.

Sources: L1 lines 1–10 and 26–80; L2 lines 4–35; L4 lines 35–74. See the [source register](research.md).
