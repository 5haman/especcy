#include "spectrum.h"
#include <algorithm>
#include <cstring>

namespace speccy {
static uint16_t word(const uint8_t* p) { return static_cast<uint16_t>(p[0] | p[1] << 8); }

const char* validate_content(const uint8_t* rom, size_t rom_size, const uint8_t* sna, size_t sna_size) {
    if (!rom || rom_size != ROM_SIZE) return "ROM must contain exactly 16384 bytes";
    if (!sna || sna_size != SNA_SIZE) return "Only 49179-byte 48K SNA snapshots are supported";
    if (sna[25] > 2 || sna[26] > 7 || (sna[19] & ~4)) return "Invalid SNA interrupt mode, border or IFF2";
    const auto sp = word(sna + 23);
    if (sp < 0x4000 || sp == 0xffff) return "SNA return address must fit in RAM";
    return nullptr;
}

const char* Spectrum48::load(const uint8_t* rom, size_t rom_size, const uint8_t* sna, size_t sna_size) {
    if (const char* error = validate_content(rom, rom_size, sna, sna_size)) return error;
    rom_ = rom;
    sna_ = sna;
    restart();
    return nullptr;
}

void Spectrum48::restart() {
    if (!sna_) return;
    std::memcpy(ram_, sna_ + 27, RAM_SIZE);
    cpu.reset();
    cpu.setRegI(sna_[0]);
    cpu.setRegHLx(word(sna_ + 1)); cpu.setRegDEx(word(sna_ + 3));
    cpu.setRegBCx(word(sna_ + 5)); cpu.setRegAFx(word(sna_ + 7));
    cpu.setRegHL(word(sna_ + 9)); cpu.setRegDE(word(sna_ + 11));
    cpu.setRegBC(word(sna_ + 13)); cpu.setRegIY(word(sna_ + 15));
    cpu.setRegIX(word(sna_ + 17)); cpu.setRegR(sna_[20]);
    cpu.setRegAF(word(sna_ + 21));
    const auto sp = word(sna_ + 23);
    cpu.setRegPC(static_cast<uint16_t>(read(sp) | read(static_cast<uint16_t>(sp + 1)) << 8));
    cpu.setRegSP(static_cast<uint16_t>(sp + 2));
    cpu.setIFF1((sna_[19] & 4) != 0); cpu.setIFF2((sna_[19] & 4) != 0);
    cpu.setIM(static_cast<Z80::IntMode>(sna_[25]));
    phase_ = 0; frames_ = 0; joystick_ = 0; border_ = sna_[26];
    std::fill(keyboard_, keyboard_ + 8, 0);
}

const char* Spectrum48::save_sna(uint8_t* out, size_t size) {
    if (!rom_ || !out || size != SNA_SIZE) return "Snapshot capture requires a loaded machine and 49179-byte output";
    // SNA has no prefix/EI-delay fields. Advance only to an instruction boundary.
    for (unsigned i = 0; i < 1024 && (cpu.getPrefixOpcode() || cpu.isPendingEI()); ++i) cpu.execute();
    if (cpu.getPrefixOpcode() || cpu.isPendingEI()) return "Cannot reach a snapshot instruction boundary";
    const auto sp = static_cast<uint16_t>(cpu.getRegSP() - 2);
    if (sp < 0x4000 || sp == 0xffff) return "SNA return address must fit in RAM";
    if (cpu.isIFF1() != cpu.isIFF2()) return "SNA cannot represent unequal IFF1 and IFF2";
    std::fill(out, out + 27, 0);
    std::memcpy(out + 27, ram_, RAM_SIZE);
    const auto put = [out](size_t at, uint16_t value) { out[at] = value & 255; out[at + 1] = value >> 8; };
    out[0] = cpu.getRegI();
    put(1, cpu.getRegHLx()); put(3, cpu.getRegDEx()); put(5, cpu.getRegBCx()); put(7, cpu.getRegAFx());
    put(9, cpu.getRegHL()); put(11, cpu.getRegDE()); put(13, cpu.getRegBC());
    put(15, cpu.getRegIY()); put(17, cpu.getRegIX()); out[19] = cpu.isIFF2() ? 4 : 0;
    out[20] = cpu.getRegR(); put(21, cpu.getRegAF()); put(23, sp);
    out[25] = static_cast<uint8_t>(cpu.getIM()); out[26] = border_;
    // Re-execute HALT after loading; SNA cannot store the halted flag.
    const auto pc = static_cast<uint16_t>(cpu.getRegPC() - (cpu.isHalted() ? 1 : 0));
    put(27 + sp - 0x4000, pc);
    return nullptr;
}

void Spectrum48::set_keyboard_row(unsigned row, uint8_t pressed) {
    if (row < 8) keyboard_[row] = pressed & 31;
}

uint8_t Spectrum48::read(uint16_t address) const {
    return address < 0x4000 ? (rom_ ? rom_[address] : 0xff) : ram_[address - 0x4000];
}
void Spectrum48::write(uint16_t address, uint8_t value) {
    if (address >= 0x4000) ram_[address - 0x4000] = value;
}

unsigned Spectrum48::contention(uint32_t t) {
    if (t < 14335 || t >= 14335 + 192 * 224) return 0;
    const unsigned col = (t - 14335) % 224;
    if (col >= 128) return 0;
    static constexpr unsigned wait[] = {6, 5, 4, 3, 2, 1, 0, 0};
    return wait[col & 7];
}
void Spectrum48::memory_cycles(uint16_t address, unsigned cycles) {
    if (address >= 0x4000 && address < 0x8000) phase_ += contention(phase());
    phase_ += cycles;
}
uint8_t Spectrum48::fetchOpcode(uint16_t address) { memory_cycles(address, 4); return read(address); }
uint8_t Spectrum48::peek8(uint16_t address) { memory_cycles(address, 3); return read(address); }
void Spectrum48::poke8(uint16_t address, uint8_t value) { memory_cycles(address, 3); write(address, value); }
uint16_t Spectrum48::peek16(uint16_t address) {
    const auto lo = peek8(address);
    return static_cast<uint16_t>(lo | peek8(static_cast<uint16_t>(address + 1)) << 8);
}
void Spectrum48::poke16(uint16_t address, RegisterPair value) {
    poke8(address, value.byte8.lo); poke8(static_cast<uint16_t>(address + 1), value.byte8.hi);
}
void Spectrum48::addressOnBus(uint16_t address, int32_t cycles) {
    for (int32_t i = 0; i < cycles; ++i) memory_cycles(address, 1);
}
void Spectrum48::interruptHandlingTime(int32_t cycles) { phase_ += static_cast<uint32_t>(cycles); }
void Spectrum48::port_cycles(uint16_t port) {
    const bool high_contended = (port & 0xc000) == 0x4000;
    if (high_contended) phase_ += contention(phase());
    ++phase_;
    if (!(port & 1)) { phase_ += contention(phase()) + 3; }
    else if (high_contended) {
        for (unsigned i = 0; i < 3; ++i) phase_ += contention(phase()) + 1;
    } else { phase_ += 3; }
}
uint8_t Spectrum48::inPort(uint16_t port) {
    port_cycles(port);
    if (!(port & 1)) {
        uint8_t value = 0xbf; // EAR low; no tape input
        for (unsigned row = 0; row < 8; ++row)
            if (!(port & (0x100u << row))) value &= ~keyboard_[row];
        return value;
    }
    if ((port & 0xff) == 0x1f) return joystick_;
    // ponytail: no floating-bus/raster-effect compatibility claim; add with a workload that needs it.
    return 0xff;
}
void Spectrum48::outPort(uint16_t port, uint8_t value) {
    port_cycles(port);
    if (!(port & 1)) border_ = value & 7;
}
void Spectrum48::run_frame(uint8_t buttons) {
    if (!rom_) return;
    joystick_ = neutral_directions(buttons & 31);
    while (phase_ < FRAME_CYCLES) cpu.execute();
    phase_ -= FRAME_CYCLES; // carry instruction overshoot; never discard emulated time
    ++frames_;
}

uint8_t neutral_directions(uint8_t buttons) {
    if ((buttons & (Left | Right)) == (Left | Right)) buttons &= ~(Left | Right);
    if ((buttons & (Up | Down)) == (Up | Down)) buttons &= ~(Up | Down);
    return buttons;
}
uint16_t rgb565(unsigned r, unsigned g, unsigned b) {
    return static_cast<uint16_t>((r >> 3) << 11 | (g >> 2) << 5 | (b >> 3));
}
static void rgb(uint8_t color, unsigned* out) {
    const unsigned v = color & 8 ? 255 : 215;
    out[0] = color & 2 ? v : 0; out[1] = color & 4 ? v : 0; out[2] = color & 1 ? v : 0;
}
uint8_t Spectrum48::pixel(unsigned x, unsigned y) const {
    const unsigned addr = ((y & 0xc0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | (x >> 3);
    const auto attr = ram_[0x1800 + (y >> 3) * 32 + (x >> 3)];
    bool ink = (ram_[addr] & (0x80 >> (x & 7))) != 0;
    if ((attr & 0x80) && (frames_ & 16)) ink = !ink;
    return static_cast<uint8_t>((ink ? attr & 7 : (attr >> 3) & 7) | ((attr & 0x40) >> 3));
}
void Spectrum48::render(uint16_t* out) const {
    unsigned bg[3]; rgb(border_, bg);
    std::fill(out, out + LCD_PIXELS, rgb565(bg[0], bg[1], bg[2]));
    for (unsigned y = 0; y < 96; ++y) {
        for (unsigned x = 0; x < 128; ++x) {
            unsigned sum[3] = {};
            for (unsigned dy = 0; dy < 2; ++dy) for (unsigned dx = 0; dx < 2; ++dx) {
                unsigned c[3]; rgb(pixel(x * 2 + dx, y * 2 + dy), c);
                for (unsigned i = 0; i < 3; ++i) sum[i] += c[i];
            }
            out[(y + 16) * 128 + x] = rgb565(sum[0] / 4, sum[1] / 4, sum[2] / 4);
        }
    }
}

uint8_t Controls::sample(uint8_t raw, uint64_t now_ms) {
    raw &= 63;
    for (unsigned i = 0; i < 6; ++i) {
        const uint8_t bit = static_cast<uint8_t>(1u << i);
        if ((raw ^ candidates_) & bit) { candidates_ ^= bit; changed_[i] = now_ms; }
        if (now_ms - changed_[i] >= 10) stable_ = static_cast<uint8_t>((stable_ & ~bit) | (candidates_ & bit));
    }
    return stable_;
}
Controls::Action Controls::update(uint8_t stable, Spectrum48& machine) {
    const uint8_t pressed = stable & ~previous_;
    previous_ = stable;
    if (wait_release_ && !stable) wait_release_ = false;
    if (pressed & Menu) {
        paused = !paused; restart_selected = false;
        wait_release_ = true; machine.release_inputs();
        return Action::None;
    }
    if (!paused) return Action::None;
    machine.release_inputs();
    const auto navigation = neutral_directions(stable) & pressed;
    if (navigation & Up) restart_selected = false;
    if (navigation & Down) restart_selected = true;
    if ((pressed & Fire) && !wait_release_) {
        paused = false; wait_release_ = true;
        if (restart_selected) { restart_selected = false; machine.restart(); return Action::Restart; }
    }
    return Action::None;
}

// Project-authored 5x7 uppercase glyphs used only by the device menu/errors.
void draw_text(uint16_t* out, unsigned x, unsigned y, const char* text, uint16_t color) {
    static constexpr const char* letters = "ACDEFILMNOPRSTUV";
    static constexpr uint8_t rows[][7] = {
        {14,17,17,31,17,17,17}, {14,17,16,16,16,17,14}, {30,17,17,17,17,17,30},
        {31,16,16,30,16,16,31}, {31,16,16,30,16,16,16}, {31,4,4,4,4,4,31},
        {16,16,16,16,16,16,31}, {17,27,21,21,17,17,17},
        {17,25,25,21,19,19,17}, {14,17,17,17,17,17,14}, {30,17,17,30,16,16,16},
        {30,17,17,30,20,18,17}, {15,16,16,14,1,1,30}, {31,4,4,4,4,4,4},
        {17,17,17,17,17,17,14}, {17,17,17,17,17,10,4}
    };
    for (; *text; ++text, x += 6) {
        const char* glyph = std::strchr(letters, *text);
        if (!glyph) continue;
        for (unsigned py = 0; py < 7 && y + py < 128; ++py)
            for (unsigned px = 0; px < 5 && x + px < 128; ++px)
                if (rows[glyph - letters][py] & (16 >> px)) out[(y + py) * 128 + x + px] = color;
    }
}
void Controls::render_menu(uint16_t* out) const {
    std::fill(out, out + LCD_PIXELS, rgb565(8, 16, 24));
    draw_text(out, 46, 24, "PAUSED", 0xffff);
    draw_text(out, 42, 52, "RESUME", restart_selected ? 0x8410 : 0xffe0);
    draw_text(out, 42, 76, "RESTART", restart_selected ? 0xffe0 : 0x8410);
}
} // namespace speccy
