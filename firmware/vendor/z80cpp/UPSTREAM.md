# z80cpp

Source: https://github.com/jsanchezv/z80cpp

Pinned commit: `2b276f0e471fa5b7f57926dc3aa3683a7f05adf5`.

The source files derive from José Luis Sánchez's
Z80Core under GPL version 3; the notices in `z80.cpp` and `z80.h` identify the
original Java commit and C++ conversion. `LICENSE` contains the upstream
Z80Core GPLv3 text. This dependency is also in ESPectrum's source lineage.

The only local core change is the marked read-only `getPrefixOpcode()` accessor
in `z80.h`, used to capture a snapshot between complete instructions.

Especcy's portable runtime and firmware integration use GPL-3.0. This does not
select a license for the pre-existing CAD or documentation, or grant permission
to distribute a Spectrum ROM or Dizzy snapshot. ESP-IDF carries its own notices.
