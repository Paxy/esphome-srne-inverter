#include "srne_inverter.h"
#include "esphome/core/log.h"

namespace esphome {
namespace srne_inverter {

static const char *const TAG = "srne_inverter";

void SrneInverter::dump_config() {
  ESP_LOGCONFIG(TAG, "SRNE Inverter:");
  ESP_LOGCONFIG(TAG, "  Address: 0x%02X", this->address_);
}

float SrneInverter::get_setup_priority() const { return setup_priority::DATA; }

void SrneInverter::update() {}

void SrneInverter::on_modbus_data(const std::vector<uint8_t> & /*data*/) {}

}  // namespace srne_inverter
}  // namespace esphome
