#include "spectrum.h"
#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

static std::vector<uint8_t> read_file(const std::string& path, size_t size) {
    std::ifstream in(path, std::ios::binary | std::ios::ate);
    if (!in || in.tellg() != static_cast<std::streamoff>(size))
        throw std::runtime_error("Cannot read expected content size: " + path);
    std::vector<uint8_t> data(size);
    in.seekg(0); in.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(size));
    if (!in) throw std::runtime_error("Content read failed: " + path);
    return data;
}
static unsigned number(const std::string& s, unsigned limit) {
    if (s.empty() || s.find_first_not_of("0123456789") != std::string::npos)
        throw std::runtime_error("Numeric arguments must be unsigned decimal integers");
    const auto n = std::stoull(s);
    if (n > limit) throw std::runtime_error("Numeric argument out of range");
    return static_cast<unsigned>(n);
}
int main(int argc, char** argv) {
    try {
        std::string rom_path, sna_path, output, save_path;
        bool start_dizzy = false;
        unsigned frames = 50, buttons = 0;
        for (int i = 1; i < argc; ++i) {
            const std::string key = argv[i];
            if (key == "--help") {
                std::cout << "speccy-host --rom ROM --snapshot SNA --output frame.ppm [--frames N] [--buttons MASK] [--start-dizzy] [--save-snapshot SNA]\n";
                return 0;
            }
            if (key == "--start-dizzy") { start_dizzy = true; continue; }
            if (++i == argc) throw std::runtime_error("Missing argument value");
            const std::string value = argv[i];
            if (key == "--rom") rom_path = value;
            else if (key == "--snapshot") sna_path = value;
            else if (key == "--output") output = value;
            else if (key == "--save-snapshot") save_path = value;
            else if (key == "--frames") frames = number(value, 1000000);
            else if (key == "--buttons") buttons = number(value, 31);
            else throw std::runtime_error("Unknown option: " + key);
        }
        if (rom_path.empty() || sna_path.empty() || output.empty())
            throw std::runtime_error("--rom, --snapshot and --output are required");
        const auto rom = read_file(rom_path, speccy::ROM_SIZE);
        const auto sna = read_file(sna_path, speccy::SNA_SIZE);
        speccy::Spectrum48 machine;
        if (const auto error = machine.load(rom.data(), rom.size(), sna.data(), sna.size()))
            throw std::runtime_error(error);
        const auto start = std::chrono::steady_clock::now();
        for (unsigned i = 0; i < frames; ++i) {
            machine.set_keyboard_row(6, start_dizzy && i < 25 ? 4 : 0); // K selects Kempston in original Dizzy.
            machine.run_frame(static_cast<uint8_t>(buttons));
        }
        machine.set_keyboard_row(6, 0);
        const auto us = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now() - start).count();
        if (!save_path.empty()) {
            std::vector<uint8_t> snapshot(speccy::SNA_SIZE);
            if (const auto error = machine.save_sna(snapshot.data(), snapshot.size())) throw std::runtime_error(error);
            std::ofstream saved(save_path, std::ios::binary);
            saved.write(reinterpret_cast<const char*>(snapshot.data()), snapshot.size());
            saved.close();
            if (!saved) throw std::runtime_error("Cannot write snapshot: " + save_path);
        }
        std::vector<uint16_t> pixels(speccy::LCD_PIXELS);
        machine.render(pixels.data());
        std::ofstream out(output, std::ios::binary);
        out << "P6\n128 128\n255\n";
        for (auto c : pixels) {
            const uint8_t rgb[] = {static_cast<uint8_t>(((c >> 11) << 3) | (c >> 13)),
                static_cast<uint8_t>(((c >> 5 & 63) << 2) | (c >> 9 & 3)),
                static_cast<uint8_t>(((c & 31) << 3) | (c >> 2 & 7))};
            out.write(reinterpret_cast<const char*>(rgb), 3);
        }
        out.close();
        if (!out) throw std::runtime_error("Cannot write frame: " + output);
        std::cout << "{\"frames\":" << machine.frames() << ",\"emulated_cycles\":" << machine.cycles()
                  << ",\"wall_us\":" << us << ",\"pc\":" << machine.cpu.getRegPC()
                  << ",\"kempston\":" << unsigned(machine.joystick()) << "}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
