#pragma once

#include "esphome/core/component.h"
#include "esphome/components/srne_modbus/srne_modbus.h"

namespace esphome {
namespace srne_inverter {

class SrneInverter : public PollingComponent, public srne_modbus::SrneModbusDevice {
 public:
  void setup() override {}
  void loop() override {}
  void update() override;
  void dump_config() override;
  float get_setup_priority() const override;

  void on_modbus_data(const std::vector<uint8_t> &data) override;
};

}  // namespace srne_inverter
}  // namespace esphome
