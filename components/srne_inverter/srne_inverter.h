#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
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

  // Block A sensors
  void set_battery_soc_sensor(sensor::Sensor *s) { battery_soc_sensor_ = s; }
  void set_battery_voltage_sensor(sensor::Sensor *s) { battery_voltage_sensor_ = s; }
  void set_battery_current_sensor(sensor::Sensor *s) { battery_current_sensor_ = s; }
  void set_pv1_voltage_sensor(sensor::Sensor *s) { pv1_voltage_sensor_ = s; }
  void set_pv1_current_sensor(sensor::Sensor *s) { pv1_current_sensor_ = s; }
  void set_pv1_power_sensor(sensor::Sensor *s) { pv1_power_sensor_ = s; }
  void set_pv2_voltage_sensor(sensor::Sensor *s) { pv2_voltage_sensor_ = s; }
  void set_pv2_current_sensor(sensor::Sensor *s) { pv2_current_sensor_ = s; }
  void set_pv2_power_sensor(sensor::Sensor *s) { pv2_power_sensor_ = s; }
  void set_pv_total_power_sensor(sensor::Sensor *s) { pv_total_power_sensor_ = s; }
  void set_charge_power_sensor(sensor::Sensor *s) { charge_power_sensor_ = s; }

 protected:
  // Block A storage
  sensor::Sensor *battery_soc_sensor_{nullptr};
  sensor::Sensor *battery_voltage_sensor_{nullptr};
  sensor::Sensor *battery_current_sensor_{nullptr};
  sensor::Sensor *pv1_voltage_sensor_{nullptr};
  sensor::Sensor *pv1_current_sensor_{nullptr};
  sensor::Sensor *pv1_power_sensor_{nullptr};
  sensor::Sensor *pv2_voltage_sensor_{nullptr};
  sensor::Sensor *pv2_current_sensor_{nullptr};
  sensor::Sensor *pv2_power_sensor_{nullptr};
  sensor::Sensor *pv_total_power_sensor_{nullptr};
  sensor::Sensor *charge_power_sensor_{nullptr};

  uint8_t request_step_{0};
  uint8_t last_request_step_{0xFF};

  void publish_state_(sensor::Sensor *s, float value);
  void decode_block_a_(const uint8_t *payload, size_t byte_count);
};

}  // namespace srne_inverter
}  // namespace esphome
