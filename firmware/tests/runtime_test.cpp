#include "spectrum.h"
#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>
using namespace speccy;

static std::vector<uint8_t> file(const std::string& path) {
    std::ifstream in(path, std::ios::binary);
    assert(in);
    return {std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>()};
}
static void setword(std::vector<uint8_t>& sna, size_t at, uint16_t value) {
    sna[at] = value & 255; sna[at + 1] = value >> 8;
}
static void load(Spectrum48& m, const std::vector<uint8_t>& rom, const std::vector<uint8_t>& sna) {
    assert(!m.load(rom.data(), rom.size(), sna.data(), sna.size()));
}
static void loader(const std::vector<uint8_t>& rom, std::vector<uint8_t> sna) {
    Spectrum48 m;
    for (size_t offset : {1,3,5,7,9,11,13,15,17,21}) setword(sna, offset, static_cast<uint16_t>(0x9100 + offset));
    sna[0] = 0x3f; sna[20] = 0x85; sna[19] = 4; sna[25] = 2;
    load(m, rom, sna);
    assert(m.cpu.getRegHLx() == 0x9101 && m.cpu.getRegDEx() == 0x9103);
    assert(m.cpu.getRegBCx() == 0x9105 && m.cpu.getRegAFx() == 0x9107);
    assert(m.cpu.getRegHL() == 0x9109 && m.cpu.getRegDE() == 0x910b);
    assert(m.cpu.getRegBC() == 0x910d && m.cpu.getRegIY() == 0x910f);
    assert(m.cpu.getRegIX() == 0x9111 && m.cpu.getRegAF() == 0x9115);
    assert(m.cpu.getRegI() == 0x3f && m.cpu.getRegR() == 0x85);
    assert(m.cpu.getIM() == Z80::IM2 && m.cpu.isIFF1() && m.cpu.isIFF2());
    assert(m.cpu.getRegPC() == 0x8000 && m.cpu.getRegSP() == 0xc002);
    m.write(0x4000, 0); m.cpu.setRegPC(0xbeef);
    assert(m.load(rom.data(), rom.size() - 1, sna.data(), sna.size()));
    assert(m.load(rom.data(), rom.size(), sna.data(), sna.size() - 1));
    assert(m.load(nullptr, ROM_SIZE, sna.data(), sna.size()));
    assert(m.load(rom.data(), rom.size(), nullptr, SNA_SIZE));
    for (auto change : {std::pair<unsigned,uint8_t>{25,3}, {26,8}, {19,1}}) {
        auto bad = sna; bad[change.first] = change.second;
        assert(m.load(rom.data(), rom.size(), bad.data(), bad.size()));
    }
    for (uint16_t sp : {0, 0x3fff, 0xffff}) {
        auto bad = sna; setword(bad, 23, sp);
        assert(m.load(rom.data(), rom.size(), bad.data(), bad.size()));
    }
    auto extra = sna; extra.push_back(0);
    assert(m.load(rom.data(), rom.size(), extra.data(), extra.size()));
    assert(m.cpu.getRegPC() == 0xbeef && m.read(0x4000) == 0); // failure is atomic
    auto end = sna; setword(end, 23, 0xfffe); setword(end, SNA_SIZE - 2, 0x1234);
    load(m, rom, end);
    assert(m.cpu.getRegPC() == 0x1234 && m.cpu.getRegSP() == 0);
    load(m, rom, sna);
    m.poke8(0x1000, 0xff);
    assert(m.read(0x1000) == rom[0x1000]);
    m.write(0x4000, 0x23); m.restart();
    assert(m.read(0x4000) == sna[27] && m.frames() == 0 && m.cycles() == 0);
}
static void capture(const std::vector<uint8_t>& rom, const std::vector<uint8_t>& sna) {
    Spectrum48 m;
    std::vector<uint8_t> saved(SNA_SIZE);
    assert(m.save_sna(saved.data(), saved.size()));
    load(m, rom, sna);
    assert(m.save_sna(nullptr, saved.size()) && m.save_sna(saved.data(), saved.size() - 1));
    assert(!m.save_sna(saved.data(), saved.size()) && saved == sna);
    m.set_keyboard_row(6, 4); m.set_keyboard_row(0, 1); m.set_keyboard_row(8, 31);
    assert(m.inPort(0xfffe) == 0xbf && m.inPort(0xbffe) == 0xbb);
    assert(m.inPort(0xfefe) == 0xbe && m.inPort(0xbefe) == 0xba);
    m.restart(); assert(m.inPort(0x00fe) == 0xbf);
    m.cpu.setIFF1(false); m.cpu.setIFF2(false);
    m.write(0x8000, 0x76); m.cpu.execute();
    assert(m.cpu.isHalted());
    assert(!m.save_sna(saved.data(), saved.size()));
    load(m, rom, saved);
    assert(m.cpu.getRegPC() == 0x8000 && m.cpu.getRegSP() == 0xc002);
    m.cpu.execute(); assert(m.cpu.isHalted() && m.cpu.getRegPC() == 0x8001);
    load(m, rom, sna); m.cpu.setIFF1(false); m.cpu.setIFF2(false);
    m.interruptHandlingTime(100);
    m.write(0x8000, 0xdd); m.write(0x8001, 0xdd); m.write(0x8002, 0x21);
    m.write(0x8003, 0x34); m.write(0x8004, 0x12);
    m.cpu.execute(); assert(m.cpu.getPrefixOpcode() == 0xdd);
    assert(!m.save_sna(saved.data(), saved.size()));
    load(m, rom, saved); assert(m.cpu.getRegIX() == 0x1234 && m.cpu.getRegPC() == 0x8005);
    m.interruptHandlingTime(100); m.write(0x8005, 0xfb); m.write(0x8006, 0);
    m.cpu.execute(); assert(m.cpu.isPendingEI());
    assert(!m.save_sna(saved.data(), saved.size()));
    load(m, rom, saved); assert(m.cpu.isIFF1() && m.cpu.isIFF2() && m.cpu.getRegPC() == 0x8007);
    m.cpu.setIFF1(false); assert(m.save_sna(saved.data(), saved.size()));
    m.cpu.setIFF2(false);
    for (uint16_t sp : {1, 0x4000, 0x4001}) {
        m.cpu.setRegSP(sp); assert(m.save_sna(saved.data(), saved.size()));
    }
    m.cpu.setRegSP(0); assert(!m.save_sna(saved.data(), saved.size()));
    load(m, rom, saved); assert(m.cpu.getRegSP() == 0);
}
static void timing(const std::vector<uint8_t>& rom, const std::vector<uint8_t>& sna) {
    Spectrum48 m; load(m, rom, sna);
    assert(m.isActiveINT());
    m.interruptHandlingTime(32); assert(!m.isActiveINT());
    assert(Spectrum48::contention(14334) == 0);
    for (unsigned i = 0; i < 8; ++i) assert(Spectrum48::contention(14335 + i) == (i < 6 ? 6-i : 0));
    assert(Spectrum48::contention(14335 + 128) == 0);
    assert(Spectrum48::contention(14335 + 224) == 6);
    assert(Spectrum48::contention(14335 + 192 * 224) == 0);
    m.restart(); m.interruptHandlingTime(14335); m.fetchOpcode(0x4000);
    assert(m.cycles() == 14345);
    m.peek8(0x8000); assert(m.cycles() == 14348);
    m.restart(); m.interruptHandlingTime(14335); m.addressOnBus(0x4000, 2);
    assert(m.cycles() == 14343);
    m.restart(); m.interruptHandlingTime(14335); m.inPort(0xfe);
    assert(m.cycles() == 14344);
    m.restart(); m.interruptHandlingTime(14335); m.inPort(0x40fe);
    assert(m.cycles() == 14345);
    m.restart(); m.interruptHandlingTime(14335); m.inPort(0x40ff);
    assert(m.cycles() == 14351);
    m.restart(); m.interruptHandlingTime(14335); m.inPort(0xff);
    assert(m.cycles() == 14339);
    m.restart();
    for (unsigned i = 0; i < 100; ++i) m.run_frame(Right | Up);
    assert(m.frames() == 100 && m.cycles() >= 100ull * FRAME_CYCLES);
    assert(m.cycles() < 100ull * FRAME_CYCLES + 128);
    assert(m.read(0x5b00) == (Right | Up)); // executed IN instruction, not just a callback
    assert(m.joystick() == (Right | Up));
    assert(m.inPort(0xff1f) == (Right | Up) && m.inPort(0xfefe) == 0xbf);
    m.run_frame(Left | Right | Fire); assert(m.read(0x5b00) == Fire);
    m.run_frame(Up | Down); assert(m.read(0x5b00) == 0);
    auto irq_rom = rom;
    const uint8_t handler[] = {0x21,0x01,0x5b,0x34,0xfb,0xed,0x4d};
    std::copy(std::begin(handler), std::end(handler), irq_rom.begin() + 0x38);
    load(m, irq_rom, sna);
    for (unsigned i = 0; i < 32; ++i) m.run_frame(0);
    assert(m.read(0x5b01) == 32); // one IM1 interrupt each emulated frame
    m.write(0xffff, 0x56);
    assert(m.peek16(0xffff) == static_cast<uint16_t>(rom[0] << 8 | 0x56));
}
static void rendering(const std::vector<uint8_t>& rom, const std::vector<uint8_t>& sna) {
    Spectrum48 m; load(m, rom, sna);
    for (uint32_t a = 0x4000; a < 0x5b00; ++a) m.write(static_cast<uint16_t>(a), 0);
    std::array<uint16_t, LCD_PIXELS> out;
    m.outPort(0xfe, 1);
    m.write(0x4000, 0x80); m.write(0x4100, 0x80); m.write(0x5800, 0x4a);
    m.render(out.data());
    assert(out[0] == rgb565(0,0,215) && out[15*128] == out[0] && out[112*128] == out[0]);
    assert(out[16*128] == 0x780f); // two bright red and two bright blue pixels
    assert(out[16*128+1] == 0x001f);
    for (auto bank : {std::array<uint16_t,3>{0x4020,0x4120,0x5820}, {0x4800,0x4900,0x5900}, {0x5000,0x5100,0x5a00}}) {
        m.write(bank[0], 0xc0); m.write(bank[1], 0xc0); m.write(bank[2], 0x42);
    }
    m.write(0x56ff, 3); m.write(0x57ff, 3); m.write(0x5aff, 0x41);
    m.render(out.data());
    assert(out[20*128] == 0xf800 && out[48*128] == 0xf800 && out[80*128] == 0xf800);
    assert(out[111*128+127] == 0x001f); // last source pixels at bottom right
    m.write(0x4001, 0xff); m.write(0x4101, 0xff); m.write(0x5801, 0xca);
    m.render(out.data()); assert(out[16*128+4] == 0xf800);
    for (unsigned i = 0; i < 16; ++i) m.run_frame(0);
    m.render(out.data()); assert(out[16*128+4] == 0x001f);
    for (unsigned i = 0; i < 16; ++i) m.run_frame(0);
    m.render(out.data()); assert(out[16*128+4] == 0xf800);
}
static void controls(const std::vector<uint8_t>& rom, const std::vector<uint8_t>& sna) {
    for (uint8_t bit = 1; bit <= Menu; bit <<= 1) {
        Controls c;
        assert(c.sample(bit, 0) == 0 && c.sample(bit, 9) == 0);
        assert(c.sample(bit, 10) == bit && c.sample(bit, 100) == bit);
        assert(c.sample(0, 110) == bit && c.sample(0, 119) == bit && c.sample(0, 120) == 0);
    }
    Controls b;
    b.sample(Right, 0); b.sample(0, 5); b.sample(Right | Down, 8);
    assert(b.sample(Down, 13) == 0);
    assert(b.sample(Right | Down, 18) == Down); // independent debounce per switch
    assert(b.sample(Right | Down, 28) == (Right | Down));
    Spectrum48 m; load(m, rom, sna);
    Controls c;
    c.update(Right, m); m.run_frame(c.game_buttons()); assert(m.joystick() == Right);
    c.update(Menu | Right, m);
    assert(c.paused && c.game_buttons() == 0 && m.joystick() == 0);
    const auto cycles = m.cycles();
    c.update(Menu | Right, m); assert(c.paused && m.cycles() == cycles);
    c.update(0, m); c.update(Fire, m);
    assert(!c.paused && c.game_buttons() == 0); // Fire cannot leak into resumed game
    c.update(Fire | Up, m); assert(c.game_buttons() == 0);
    c.update(0, m); c.update(Up | Right, m); assert(c.game_buttons() == (Up | Right));
    c.update(Left | Right | Up | Down | Fire, m); assert(c.game_buttons() == Fire);
    c.update(0, m); c.update(Menu, m); c.update(0, m); c.update(Down, m);
    assert(c.restart_selected);
    c.update(0, m); c.update(Up | Down, m); assert(c.restart_selected);
    c.update(0, m);
    assert(c.update(Fire, m) == Controls::Action::Restart);
    assert(!c.paused && m.frames() == 0 && m.cpu.getRegPC() == 0x8000 && c.game_buttons() == 0);
    c.update(0, m); c.update(Menu, m); c.update(0, m); c.update(Menu, m);
    assert(!c.paused && c.game_buttons() == 0); // Menu itself resumes
    std::array<uint16_t,LCD_PIXELS> out;
    c.render_menu(out.data());
    assert(out[0] == rgb565(8,16,24));
}
int main(int argc, char** argv) {
    assert(argc == 2);
    const std::string dir = argv[1];
    const auto rom = file(dir + "/spectrum48.rom"), sna = file(dir + "/game48.sna");
    loader(rom,sna); capture(rom,sna); timing(rom,sna); rendering(rom,sna); controls(rom,sna);
    std::cout << "PASS: loader/capture, keyboard, bus, timing/interrupts, rendering/FLASH, debounce and menu\n";
}
