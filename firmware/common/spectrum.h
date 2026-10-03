#pragma once
#include <cstddef>
#include <cstdint>
#include "z80.h"

namespace speccy {
constexpr size_t ROM_SIZE = 16384;
constexpr size_t RAM_SIZE = 49152;
constexpr size_t SNA_SIZE = 27 + RAM_SIZE;
constexpr unsigned FRAME_CYCLES = 69888;
constexpr unsigned FRAME_US = 19968;
constexpr unsigned LCD_PIXELS = 128 * 128;
enum Button : uint8_t { Right = 1, Left = 2, Down = 4, Up = 8, Fire = 16, Menu = 32 };

const char* validate_content(const uint8_t* rom, size_t rom_size,
                             const uint8_t* sna, size_t sna_size);
uint8_t neutral_directions(uint8_t buttons);
uint16_t rgb565(unsigned r, unsigned g, unsigned b);
void draw_text(uint16_t* pixels, unsigned x, unsigned y, const char* text, uint16_t color);

// Content storage must outlive the machine. ESP32 content stays in mapped flash.
class Spectrum48 final : public Z80operations {
public:
    Spectrum48() : cpu(this) {}
    Spectrum48(const Spectrum48&) = delete;
    Spectrum48& operator=(const Spectrum48&) = delete;
    const char* load(const uint8_t* rom, size_t rom_size, const uint8_t* sna, size_t sna_size);
    void restart();
    const char* save_sna(uint8_t* out, size_t size);
    void set_keyboard_row(unsigned row, uint8_t pressed);
    void run_frame(uint8_t buttons);
    void render(uint16_t* pixels) const;
    uint8_t read(uint16_t address) const;
    void write(uint16_t address, uint8_t value);
    uint64_t frames() const { return frames_; }
    uint64_t cycles() const { return frames_ * FRAME_CYCLES + phase_; }
    uint32_t phase() const { return phase_ >= FRAME_CYCLES ? phase_ - FRAME_CYCLES : phase_; }
    uint8_t border() const { return border_; }
    uint8_t joystick() const { return joystick_; }
    void release_inputs() { joystick_ = 0; }
    static unsigned contention(uint32_t phase);

    uint8_t fetchOpcode(uint16_t address) override;
    uint8_t peek8(uint16_t address) override;
    void poke8(uint16_t address, uint8_t value) override;
    uint16_t peek16(uint16_t address) override;
    void poke16(uint16_t address, RegisterPair value) override;
    uint8_t inPort(uint16_t port) override;
    void outPort(uint16_t port, uint8_t value) override;
    void addressOnBus(uint16_t address, int32_t cycles) override;
    void interruptHandlingTime(int32_t cycles) override;
    bool isActiveINT() override { return phase() < 32; }

    Z80 cpu;
private:
    void memory_cycles(uint16_t address, unsigned cycles);
    void port_cycles(uint16_t port);
    uint8_t pixel(unsigned x, unsigned y) const;
    const uint8_t* rom_ = nullptr;
    const uint8_t* sna_ = nullptr;
    uint8_t ram_[RAM_SIZE] = {};
    uint32_t phase_ = 0;
    uint64_t frames_ = 0;
    uint8_t joystick_ = 0;
    uint8_t keyboard_[8] = {};
    uint8_t border_ = 0;
};

// Shared host/ESP32 input state; timestamps are monotonic milliseconds.
struct Controls {
    uint8_t sample(uint8_t raw, uint64_t now_ms);
    enum class Action { None, Restart };
    Action update(uint8_t stable, Spectrum48& machine);
    uint8_t game_buttons() const { return paused || wait_release_ ? 0 : neutral_directions(previous_ & 31); }
    void render_menu(uint16_t* pixels) const;
    bool paused = false;
    bool restart_selected = false;
private:
    uint8_t candidates_ = 0, stable_ = 0, previous_ = 0;
    uint64_t changed_[6] = {};
    bool wait_release_ = false;
};
} // namespace speccy
