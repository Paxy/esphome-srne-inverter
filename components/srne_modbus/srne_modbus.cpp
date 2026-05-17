#include "srne_modbus.h"
#include "esphome/core/log.h"

namespace esphome {
namespace srne_modbus {

static const char *const TAG = "srne_modbus";

void SrneModbus::setup() {
  if (this->flow_control_pin_ != nullptr) {
    this->flow_control_pin_->setup();
  }
}

void SrneModbus::loop() {}

void SrneModbus::dump_config() {
  ESP_LOGCONFIG(TAG, "SRNE Modbus:");
  ESP_LOGCONFIG(TAG, "  Flow control pin: %s", YESNO(this->flow_control_pin_ != nullptr));
}

float SrneModbus::get_setup_priority() const { return setup_priority::DATA; }

uint16_t crc16_modbus(const uint8_t *data, uint16_t len) {
  uint16_t crc = 0xFFFF;
  for (uint16_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x0001) {
        crc = (crc >> 1) ^ 0xA001;
      } else {
        crc >>= 1;
      }
    }
  }
  return crc;
}

void SrneModbus::send(uint8_t address, uint8_t function, uint16_t start_register, uint16_t num_registers) {
  ModbusRequest request{address, function, start_register, num_registers, {}};
  this->request_queue_.push(request);
}

void SrneModbus::send_next_request_() {}

bool SrneModbus::parse_modbus_byte_(uint8_t /*byte*/) { return true; }

}  // namespace srne_modbus
}  // namespace esphome
