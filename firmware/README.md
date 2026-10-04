# Speccy 48K bench firmware

This phase supplies a host-tested Spectrum 48K runtime and ESP32 builds for the
project-authored diagnostic and **Dizzy: The Ultimate Cartoon Adventure (1987)**.
The selected target is ESP32-WROOM-32E-N4 with no PSRAM. Hardware operation has
not been tested. This firmware prepares the bench work; it does not validate the
custom carrier or the compact enclosure.

## Build and check on a host

Run from the repository root with CMake, a C++14 compiler and Python 3 installed:

```sh
cmake -S firmware -B firmware/build-host -DSPECCY_HOST=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build firmware/build-host
ctest --test-dir firmware/build-host --output-on-failure
firmware/build-host/speccy-host --rom firmware/build-host/content/spectrum48.rom --snapshot firmware/build-host/content/game48.sna --frames 50 --buttons 9 --output firmware/build-host/frame.ppm
```

Address and undefined-behavior sanitizers are enabled by default. The three
CTest suites cover loading and capture, registers, bus contention, interrupts,
frame timing, pixels and FLASH, controls/menu transitions, CLI errors, content
packaging and offline conversion. These tests need no commercial assets.
`-DSPECCY_SANITIZE=OFF` is available for compilers without sanitizer support.

The host writes a 128 × 128 RGB PPM and prints JSON metrics. `--frames` counts
emulated frames, without wall-clock pacing. `--buttons` holds a Kempston mask:
Right=1, Left=2, Down=4, Up=8, Fire=16. Opposing directions cancel independently;
diagonal directions and Fire can remain held together.

## Prepare local Dizzy content

Keep a 16,384-byte original Spectrum 48K ROM and a 48K snapshot locally. Put
them in the ignored `firmware/private/` directory. No ROM, game, game screenshot
or resulting game firmware image is distributed by this repository.

The device accepts only a **49,179-byte 48K SNA**. If the source is an extended
48K Z80 v2/v3 snapshot, convert it offline:

```sh
python3 firmware/tools/z80_to_sna.py firmware/private/dizzy.z80 firmware/private/dizzy-title.sna
firmware/build-host/speccy-host --rom firmware/private/spectrum48.rom --snapshot firmware/private/dizzy-title.sna --start-dizzy --frames 150 --save-snapshot firmware/private/dizzy.sna --output firmware/private/dizzy-first-level.ppm
```

`--start-dizzy` holds **K** for the first 25 frames, then releases it. The original
game's manual assigns K to start with Kempston. Inspect the resulting first
level before using `dizzy.sna`; another source snapshot can start in a different
state. For an existing SNA title screen, use it directly in the second command.
For a SNA already in play with Kempston, skip both preparation steps.

The converter rejects 128K/16K and paged Interface 1 states, unsupported headers,
missing/duplicate pages, invalid compression and interrupt/stack states that SNA
cannot represent. Capture finishes any incomplete prefix or EI delay and saves
a HALT so it can be re-entered on load. Snapshot capture is a host preparation
tool. There is no device save-state feature or device keyboard.

`tools/content.py` checks sizes, interrupt mode, IFF2 encoding, border and the
RAM return-address location. It writes a SHA256 manifest in each build's
`content/` directory. These checks cannot identify a game or prove that arbitrary
snapshot data is semantically correct. Use known sources and review the host
output. The local validation sources and hashes are recorded in
[research](../docs/research.md) and [verification](../docs/verification.md).

## Build for ESP32

Use **ESP-IDF v5.4.4**, pinned to `296b6eab9445fd720e71aecab961e2d3fbca9944`.
The build rejects other IDF versions. Install it outside this repository:

```sh
mkdir -p ~/esp
git clone --branch v5.4.4 --depth 1 --recursive https://github.com/espressif/esp-idf.git ~/esp/esp-idf-v5.4.4
~/esp/esp-idf-v5.4.4/install.sh esp32
source ~/esp/esp-idf-v5.4.4/export.sh
```

From `firmware/`, the default build generates the original diagnostic content:

```sh
idf.py -B build-esp32 build
idf.py -B build-esp32 size
```

Build Dizzy separately, replacing the two content paths with absolute paths:

```sh
idf.py -B build-dizzy -D SDKCONFIG="$PWD/build-dizzy/sdkconfig" -D SPECCY_CONTENT=dizzy -D SPECCY_ROM=/absolute/path/spectrum48.rom -D SPECCY_SNA=/absolute/path/dizzy.sna build
idf.py -B build-dizzy size
```

Content files are embedded in mapped flash. The standard single-app partition
has a 1 MiB factory application at `0x10000`. There is no filesystem, OTA, SD
loader or network service. Changing content requires a rebuild and UART flash.
The defaults use 4 MB flash, 240 MHz CPU, an 8 KiB main-task stack on CPU1 and a
1 kHz scheduler tick. Wi-Fi, Bluetooth and PSRAM components are excluded; enabled
configuration symbols also cause a compile error.

## Bench wiring

Use a WROOM-32E-N4 development setup outside the case. A development board is
only a bench fixture; the product still requires the custom carrier. Supply
the LCD from **3.3 V**, use common ground, and connect each switch between its
GPIO and ground. Firmware enables internal pull-ups. Use one power source for
the bench; the final pogo fixture's 3V3 policy remains D-007.

| Connection | ESP32 GPIO |
| --- | --- |
| LCD DIN / MOSI | 23 |
| LCD CLK | 18 |
| LCD CS | 21 |
| LCD DC | 22 |
| LCD RST | 19 |
| LCD BL | 25 |
| Up / Down | 26 / 27 |
| Left / Right | 32 / 33 |
| Fire / Menu | 13 / 14 |

This allocation avoids flash, UART0 and boot-strapping pins. It is a firmware
bench binding, not a released PCB netlist or a physical LCD pad-order drawing.
Confirm the purchased module's labels. The driver uses the manufacturer's
register sequence, X+2/Y+3 window offset, RGB565 high-byte-first data, SPI mode 0
and an initial 20 MHz clock. Adjust `SPECCY_SPI_CLOCK_MHZ` with `idf.py menuconfig`
only after observing the actual display and wiring.

## Flash and recovery

With the bench connected and the ESP-IDF environment active, run from `firmware/`:

```sh
idf.py -B build-esp32 -p /dev/cu.YOUR_ADAPTER flash monitor
```

Use `-B build-dizzy` for the game. Exit the monitor with Ctrl+]. If the adapter
does not control reset/boot, hold GPIO0 low, pulse EN low then high, start the
flash command, and release GPIO0 after connection. UART0 device TX is GPIO1 and
device RX is GPIO3; cross them to adapter RX/TX with 3.3 V logic and common ground.
The [electrical handoff](../hardware/electronics/README.md) now defines the
numbered underside interface and manual BOOT/RESET reference circuit. Pogo
3V3 is sense only; the fixture has independent local power and gated UART in
both directions. Use esptool without automatic reset for that fixture. Probe
mechanics and powered/unpowered, flash and recovery cases remain untested.

Bad or missing content fails the build. Invalid embedded content stops emulation,
logs the reason and shows `CONTENT ERROR` when the display is available. Display
or allocation errors stop with a UART error. Correct the cause and reflash.
After interrupted programming, return to the serial bootloader and flash the
complete image again. Power loss and Menu → Restart both return to the compiled
snapshot; game progress is not persistent. These recovery paths require bench
validation through the actual programmer.

## Runtime and bench acceptance

Each game frame executes **69,888 T-states per 19,968 µs** (about 50.08 Hz).
Instruction overshoot carries into the next frame. Memory and port contention
use the 48K timing pattern. The LCD renders every second tick (about 25.04 fps).
Each 2 × 2 source block is averaged into RGB565, producing 128 × 96 pixels with
16 border-colored rows above and below. Attributes include BRIGHT and FLASH.
One internal DMA framebuffer uses 32,768 bytes. Rendering regenerates it before
the SPI transfer swaps byte order in place.

Buttons use independent 10 ms debounce. Menu pauses emulation and isolates game
inputs. Up selects Resume; Down selects Restart; Fire activates the selection.
Menu also resumes. After either return, all buttons must be released before
game input resumes. Held Menu does not repeat. Restart reloads the prepared SNA.

UART logs mode and allocation sizes at boot, then a JSON report every five
seconds: elapsed boot time, emulated/LCD frame counts, overruns, maximum core,
render and SPI times, the current Kempston mask, and free/minimum/largest internal heap blocks. Restart
logs `event=restart` and resets the machine frame count. Compare report deltas
within one uninterrupted run. Overruns preserve emulated work; large delays
rebase the wall-clock deadline and remain visible in the count.

At the bench, check in this order:

1. Flash the diagnostic. Check orientation, all four edges, normal/bright colors,
   and border. The bottom R/L/D/U/F indicators turn yellow for each bit read by
   the emulated diagnostic. Check every button, held input and combination.
2. Check pause/resume/restart and that held buttons do not leak into the game.
3. Flash the prepared Dizzy state. Check walking, jumping, simultaneous controls
   and Fire's pickup/use action near an appropriate item. Compare readability
   with the host frame on the actual 0.85-inch LCD.
4. Capture uninterrupted UART reports for the agreed run duration. Check about
   50.08 game frames and 25.04 LCD frames per second, overruns and stable heap.
   Record SPI timing, input latency, watchdog behavior, voltage and temperature.
5. Check cold boot, power removal, content error and interrupted-flash recovery
   through the intended fixture. Record sample revisions and unresolved failures.

The hardware gate is Beads `op-se7.2`. Physical evidence is still needed for
timing, memory headroom, LCD behavior, action controls, power, heat and assembly.
There is no floating-bus, raster-effect, tape, sound or 128K compatibility claim.

## Verified software evidence and licenses

On 2026-10-03, AppleClang 21 host builds passed all three sanitizer-enabled
CTest suites. Original Dizzy reached the first level, responded to Left/Right,
Up and Right+Up, and ran 15,000 frames (299.52 emulated seconds) without sanitizer
errors. Fire's bit path is covered by the diagnostic; an actual item-use scenario
remains part of the game bench check.

ESP-IDF v5.4.4 builds passed for both modes with no compiler/configuration
warnings. Diagnostic/game binaries are **266,720 / 266,528 bytes**. The game build
reports **62,676 bytes static DRAM** and **55,590 bytes IRAM**. The ROM/SNA symbols
are in mapped flash with their exact sizes; Wi-Fi, Bluetooth and PSRAM components
and initialization symbols are absent. Static size does not measure runtime
heap, the DMA allocation or real-time performance.

New firmware code uses [GPL-3.0](LICENSE). The pinned Z80 core and its single
local accessor change are described in [UPSTREAM.md](vendor/z80cpp/UPSTREAM.md).
The manufacturer's driver permission notice is retained in
[NOTICE](vendor/waveshare/NOTICE). This selects no license for the pre-existing
CAD or documentation and grants no ROM/game redistribution permission.
