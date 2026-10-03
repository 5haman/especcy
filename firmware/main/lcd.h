#pragma once
#include <cstdint>
#include "esp_err.h"
esp_err_t lcd_init();
// Buffer is DMA-capable and is converted in-place to the LCD's high-byte-first order.
esp_err_t lcd_frame(uint16_t* pixels);
