#include "srne_inverter.h"
#include "esphome/core/log.h"

namespace esphome {
namespace srne_inverter {

static const char *const TAG = "srne_inverter";

static const uint8_t FUNCTION_READ_HOLDING = 0x03;

// Block A: controller / PV — 0x0100..0x0111 (18 regs, 36 bytes)
static const uint16_t REG_BLOCK_A_START = 0x0100;
static const uint16_t REG_BLOCK_A_COUNT = 0x12;
static const uint8_t BLOCK_A_BYTE_COUNT = 0x24;

void SrneInverter::dump_config() {
  ESP_LOGCONFIG(TAG, "SRNE Inverter:");
  ESP_LOGCONFIG(TAG, "  Address: 0x%02X", this->address_);
  LOG_SENSOR("  ", "Battery SOC", this->battery_soc_sensor_);
  LOG_SENSOR("  ", "Battery V", this->battery_voltage_sensor_);
  LOG_SENSOR("  ", "Battery A", this->battery_current_sensor_);
  LOG_SENSOR("  ", "PV1 V", this->pv1_voltage_sensor_);
  LOG_SENSOR("  ", "PV1 A", this->pv1_current_sensor_);
  LOG_SENSOR("  ", "PV1 W", this->pv1_power_sensor_);
  LOG_SENSOR("  ", "PV2 V", this->pv2_voltage_sensor_);
  LOG_SENSOR("  ", "PV2 A", this->pv2_current_sensor_);
  LOG_SENSOR("  ", "PV2 W", this->pv2_power_sensor_);
  LOG_SENSOR("  ", "PV Total W", this->pv_total_power_sensor_);
  LOG_SENSOR("  ", "Charge W", this->charge_power_sensor_);
}

float SrneInverter::get_setup_priority() const { return setup_priority::DATA; }

void SrneInverter::update() {
  // For now, only block A. Block B/C/D/E added in later tasks.
  this->last_request_step_ = 0;
  this->send(FUNCTION_READ_HOLDING, REG_BLOCK_A_START, REG_BLOCK_A_COUNT);
}

void SrneInverter::on_modbus_data(const std::vector<uint8_t> &data) {
  if (data.size() < 5) return;

  uint8_t address = data[0];
  uint8_t function = data[1];

  if (address != this->address_) return;

  if ((function & 0x80) != 0) {
    ESP_LOGW(TAG, "Modbus error response: 0x%02X", data[2]);
    return;
  }

  if (function != FUNCTION_READ_HOLDING) {
    return;
  }

  uint8_t byte_count = data[2];
  if (data.size() < (size_t)(3 + byte_count + 2)) {
    ESP_LOGW(TAG, "Truncated response");
    return;
  }

  const uint8_t *payload = data.data() + 3;

  // Dispatch by (request_step, byte_count). For now only block A.
  if (this->last_request_step_ == 0 && byte_count == BLOCK_A_BYTE_COUNT) {
    this->decode_block_a_(payload, byte_count);
  } else {
    ESP_LOGW(TAG, "Unexpected response: step=%u byte_count=%u",
             this->last_request_step_, byte_count);
  }
}

static inline uint16_t get_u16(const uint8_t *p, size_t i) {
  return (uint16_t(p[i]) << 8) | uint16_t(p[i + 1]);
}
static inline int16_t get_i16(const uint8_t *p, size_t i) {
  return (int16_t) get_u16(p, i);
}

void SrneInverter::decode_block_a_(const uint8_t *p, size_t /*byte_count*/) {
  // Layout (each register is 2 bytes; offset = (reg - 0x0100) * 2)
  // 0x0100 SOC | 0x0101 V x0.1 | 0x0102 I x0.1 signed | ...
  this->publish_state_(this->battery_soc_sensor_, (float) get_u16(p, 0));
  this->publish_state_(this->battery_voltage_sensor_, get_u16(p, 2) * 0.1f);
  this->publish_state_(this->battery_current_sensor_, get_i16(p, 4) * 0.1f);
  // 0x0103 device temp (skip), 0x0104-0x0106 DC load (gray, skip)
  // 0x0107 PV1 V, 0x0108 PV1 I, 0x0109 PV1 W
  this->publish_state_(this->pv1_voltage_sensor_, get_u16(p, 14) * 0.1f);
  this->publish_state_(this->pv1_current_sensor_, get_u16(p, 16) * 0.1f);
  uint16_t pv1_w = get_u16(p, 18);
  this->publish_state_(this->pv1_power_sensor_, (float) pv1_w);
  // 0x010A DC load on/off (skip), 0x010B charge_state (handled in text_sensor task)
  // 0x010C-0x010D fault msg (skip), 0x010E charge_power
  this->publish_state_(this->charge_power_sensor_, (float) get_u16(p, 28));
  // 0x010F PV2 V, 0x0110 PV2 I, 0x0111 PV2 W
  this->publish_state_(this->pv2_voltage_sensor_, get_u16(p, 30) * 0.1f);
  this->publish_state_(this->pv2_current_sensor_, get_u16(p, 32) * 0.1f);
  uint16_t pv2_w = get_u16(p, 34);
  this->publish_state_(this->pv2_power_sensor_, (float) pv2_w);
  this->publish_state_(this->pv_total_power_sensor_, (float) (pv1_w + pv2_w));
}

void SrneInverter::publish_state_(sensor::Sensor *s, float value) {
  if (s != nullptr && !std::isnan(value)) {
    s->publish_state(value);
  }
}

}  // namespace srne_inverter
}  // namespace esphome
