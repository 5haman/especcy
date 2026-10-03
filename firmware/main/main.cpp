#include "spectrum.h"
#include "lcd.h"
#include <algorithm>
#include <cinttypes>
#include "driver/gpio.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

#if defined(CONFIG_BT_ENABLED) || defined(CONFIG_SPIRAM) || defined(CONFIG_ESP_WIFI_ENABLED)
#error "Speccy bench firmware excludes Bluetooth, PSRAM and the Wi-Fi component"
#endif

extern const uint8_t rom_start[] asm("_binary_speccy_rom_start");
extern const uint8_t rom_end[] asm("_binary_speccy_rom_end");
extern const uint8_t sna_start[] asm("_binary_speccy_sna_start");
extern const uint8_t sna_end[] asm("_binary_speccy_sna_end");
namespace {
const char* TAG = "speccy";
speccy::Spectrum48 machine; // internal DRAM, never on the FreeRTOS stack
speccy::Controls controls;
uint16_t* pixels;
constexpr gpio_num_t inputs[] = {GPIO_NUM_33,GPIO_NUM_32,GPIO_NUM_27,GPIO_NUM_26,GPIO_NUM_13,GPIO_NUM_14};
void poll_controls() {
    uint8_t raw = 0;
    for (unsigned i = 0; i < 6; ++i) if (!gpio_get_level(inputs[i])) raw |= 1u << i;
    if (controls.update(controls.sample(raw, static_cast<uint64_t>(esp_timer_get_time() / 1000)), machine)
        == speccy::Controls::Action::Restart) ESP_LOGI(TAG, "event=restart");
}
[[noreturn]] void stop(const char* error, bool screen) {
    ESP_LOGE(TAG, "%s; emulation stopped. Correct content/wiring and reflash through UART.", error);
    if (screen && pixels) {
        std::fill(pixels, pixels + speccy::LCD_PIXELS, speccy::rgb565(80,0,0));
        speccy::draw_text(pixels, 24, 56, "CONTENT ERROR", 0xffff);
        lcd_frame(pixels);
    }
    for (;;) vTaskDelay(pdMS_TO_TICKS(1000));
}
}
extern "C" void app_main() {
    gpio_config_t buttons = {};
    for (auto pin : inputs) buttons.pin_bit_mask |= 1ULL << pin;
    buttons.mode = GPIO_MODE_INPUT; buttons.pull_up_en = GPIO_PULLUP_ENABLE;
    if (const auto error = gpio_config(&buttons)) stop(esp_err_to_name(error), false);
    pixels = static_cast<uint16_t*>(heap_caps_malloc(speccy::LCD_PIXELS * 2, MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA));
    if (!pixels) stop("No internal DMA framebuffer memory", false);
    if (const auto error = lcd_init()) stop(esp_err_to_name(error), false);
    if (const auto error = machine.load(rom_start, rom_end-rom_start, sna_start, sna_end-sna_start)) stop(error, true);
    ESP_LOGI(TAG, "mode=%s machine_bytes=%u framebuffer_bytes=%u spi_mhz=%d radios=off psram=off",
             SPECCY_DIAGNOSTIC ? "diagnostic" : "dizzy", unsigned(sizeof(machine)),
             unsigned(speccy::LCD_PIXELS * 2), CONFIG_SPECCY_SPI_CLOCK_MHZ);
    uint64_t ticks = 0, lcd_frames = 0, overruns = 0;
    int64_t next_tick = esp_timer_get_time(), report = next_tick;
    int64_t max_core_us = 0, max_render_us = 0, max_spi_us = 0;
    for (;;) {
        poll_controls();
        if (!controls.paused) {
            const auto start = esp_timer_get_time();
            machine.run_frame(controls.game_buttons());
            max_core_us = std::max(max_core_us, esp_timer_get_time()-start);
        }
        if ((ticks++ & 1) == 0) {
            const auto render_start = esp_timer_get_time();
            if (controls.paused) controls.render_menu(pixels);
            else {
                machine.render(pixels);
                if (SPECCY_DIAGNOSTIC) {
                    speccy::draw_text(pixels, 40, 4, "TEST ROM", 0xffff);
                    const char* labels[] = {"R", "L", "D", "U", "F"};
                    const auto mask = machine.read(0x5b00); // Written by the diagnostic's emulated IN.
                    for (unsigned i = 0; i < 5; ++i)
                        speccy::draw_text(pixels, 36 + i * 12, 116, labels[i], mask & (1u << i) ? 0xffe0 : 0x8410);
                }
            }
            max_render_us = std::max(max_render_us, esp_timer_get_time()-render_start);
            const auto start = esp_timer_get_time();
            if (const auto error = lcd_frame(pixels)) stop(esp_err_to_name(error), false);
            max_spi_us = std::max(max_spi_us, esp_timer_get_time()-start);
            ++lcd_frames;
        }
        next_tick += speccy::FRAME_US;
        const auto now = esp_timer_get_time();
        if (now > next_tick) {
            ++overruns;
            // ponytail: bounded catch-up; preserve CPU cycles and report slow hardware instead of skipping game frames.
            if (now-next_tick >= speccy::FRAME_US) next_tick = now;
        }
        if (now-report >= 5000000) {
            ESP_LOGI(TAG, "{\"wall_us\":%" PRId64 ",\"emu_frames\":%" PRIu64 ",\"lcd_frames\":%" PRIu64
                ",\"overruns\":%" PRIu64 ",\"max_core_us\":%" PRId64 ",\"max_spi_us\":%" PRId64
                ",\"max_render_us\":%" PRId64 ",\"kempston\":%u"
                ",\"free_internal\":%u,\"min_internal\":%u,\"largest_internal\":%u}",
                now, machine.frames(), lcd_frames, overruns, max_core_us, max_spi_us, max_render_us, unsigned(machine.joystick()),
                unsigned(heap_caps_get_free_size(MALLOC_CAP_INTERNAL)),
                unsigned(heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL)),
                unsigned(heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL)));
            report = now;
        }
        // One millisecond yields also allow idle/watchdog tasks to run after an overrun.
        do { poll_controls(); vTaskDelay(pdMS_TO_TICKS(1)); } while (esp_timer_get_time() < next_tick);
    }
}
