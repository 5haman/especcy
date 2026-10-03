#include "lcd.h"
#include "spectrum.h"
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

namespace {
constexpr gpio_num_t DC = GPIO_NUM_22, RST = GPIO_NUM_19, BL = GPIO_NUM_25;
spi_device_handle_t device;
esp_err_t send(bool data, const uint8_t* bytes, size_t size) {
    if (const auto error = gpio_set_level(DC, data)) return error;
    spi_transaction_t tx = {};
    tx.length = size * 8; tx.tx_buffer = bytes;
    return spi_device_polling_transmit(device, &tx);
}
esp_err_t command(uint8_t cmd, const uint8_t* data = nullptr, size_t size = 0) {
    if (const auto error = send(false, &cmd, 1)) return error;
    return size ? send(true, data, size) : ESP_OK;
}
}
esp_err_t lcd_init() {
    gpio_config_t pins = {};
    pins.pin_bit_mask = (1ULL << DC) | (1ULL << RST) | (1ULL << BL);
    pins.mode = GPIO_MODE_OUTPUT;
    if (const auto error = gpio_config(&pins)) return error;
    gpio_set_level(BL, 0);
    gpio_set_level(RST, 1); vTaskDelay(pdMS_TO_TICKS(100));
    gpio_set_level(RST, 0); vTaskDelay(pdMS_TO_TICKS(100));
    gpio_set_level(RST, 1); vTaskDelay(pdMS_TO_TICKS(100));
    spi_bus_config_t bus = {};
    bus.mosi_io_num = 23; bus.miso_io_num = -1; bus.sclk_io_num = 18;
    bus.quadwp_io_num = -1; bus.quadhd_io_num = -1;
    bus.max_transfer_sz = speccy::LCD_PIXELS * 2;
    if (const auto error = spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO)) return error;
    spi_device_interface_config_t cfg = {};
    cfg.clock_speed_hz = CONFIG_SPECCY_SPI_CLOCK_MHZ * 1000000;
    cfg.mode = 0; cfg.spics_io_num = 21; cfg.queue_size = 1;
    if (const auto error = spi_bus_add_device(SPI2_HOST, &cfg, &device)) return error;
    if (const auto error = command(0x11)) return error;
    vTaskDelay(pdMS_TO_TICKS(120));
    // Waveshare SKU 26117 initialization. Permission notice: vendor/waveshare/NOTICE.
    struct Register { uint8_t command, size, data[16]; };
    static const Register init[] = {
        {0xb1,3,{5,0x3c,0x3c}}, {0xb2,3,{5,0x3c,0x3c}},
        {0xb3,6,{5,0x3c,0x3c,5,0x3c,0x3c}}, {0xb4,1,{3}},
        {0xc0,3,{0xa4,4,0x84}}, {0xc1,1,{0xc8}}, {0xc2,2,{0x0d,0}},
        {0xc3,2,{0x8d,0x2a}}, {0xc4,2,{0x8d,0xee}}, {0xc5,1,{0x1d}},
        {0xe0,16,{0x0c,0x0a,6,0,0x1a,0x11,0x0b,0x0a,0x0b,0x0c,0x19,0x33,0,6,2,0x10}},
        {0xe1,16,{0x0d,0x0f,3,0,0x11,0x0a,6,8,9,0x0d,0x1c,0x3a,0,9,7,0x10}},
        {0x35,1,{0}}, {0x3a,1,{5}}, {0x21,0,{}}, {0x36,1,{0xc8}}, {0x29,0,{}}
    };
    for (const auto& r : init) if (const auto error = command(r.command, r.data, r.size)) return error;
    return gpio_set_level(BL, 1);
}
esp_err_t lcd_frame(uint16_t* pixels) {
    // Inclusive end coordinates: manufacturer window offset is X+2, Y+3.
    static const uint8_t x[] = {0,2,0,129}, y[] = {0,3,0,130};
    if (const auto error = command(0x2a, x, sizeof(x))) return error;
    if (const auto error = command(0x2b, y, sizeof(y))) return error;
    if (const auto error = command(0x2c)) return error;
    for (unsigned i = 0; i < speccy::LCD_PIXELS; ++i)
        pixels[i] = static_cast<uint16_t>(pixels[i] >> 8 | pixels[i] << 8);
    return send(true, reinterpret_cast<const uint8_t*>(pixels), speccy::LCD_PIXELS * 2);
}
