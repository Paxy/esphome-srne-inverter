# ESPHome SRNE Inverter Component — Design

**Status:** approved
**Date:** 2026-05-16
**Source protocol doc:** `srne-hybrid-solar-inverter-modbus-protocol-v1-7.pdf` (V1.7, 2022-07-04)

## Goal

A read-only ESPHome external component that talks to an SRNE hybrid solar inverter over RS485/Modbus RTU and publishes its data as ESPHome sensors / binary sensors / text sensors. Control (writes) is explicitly out of scope for V1.

The component mirrors the architecture of [esphome-eg4-bms](https://github.com/RAR/esphome-eg4-bms) and [esphome-ecoworthy-bms](https://github.com/RAR/esphome-ecoworthy-bms): a thin Modbus RTU hub implemented directly in C++ (not the built-in ESPHome `modbus_controller`), and a device component that owns the register layout and decoding.

## Why not the built-in `modbus_controller`?

Same rationale as the EG4/Ecoworthy components:
- Polling cadence and request batching are controlled in C++ so we can pack contiguous useful registers into single transactions and stay inside SRNE's 32-register read limit.
- Packed fields (status enums, fault bitmasks, ASCII strings stored 1 byte per register) are decoded natively instead of via long lambdas in YAML.
- The user can wire up sensors by name (`battery_soc:`) instead of by register address.

## Protocol summary (from V1.7)

- 9600 8N1, master/slave, star wiring, up to 254 slaves
- Slave address range `0x01`–`0xFE`. Broadcast `0x00`. Universal `0xFF` (one-to-one only).
- Functions: `0x03` read holding, `0x06` write single, `0x10` write multiple
- Error responses: function | `0x80` (e.g. `0x83`, `0x86`, `0x90`) followed by 1-byte error code
- Standard Modbus CRC16 (poly `0xA001`, init `0xFFFF`), **transmitted low byte then high byte** on the wire
- Max **32 registers** per read or write
- 32-bit values: low word at low register address (little-endian by register)
- Common unit multipliers: V ×10, A ×10, Hz ×100, °C ×10 (signed), W ×1, kWh ×10, AH ×1
- "Battery setup voltage" is always normalised to 12 V (actual value = register / 10 × nominal/12). Not used by any V1 sensor.

## Architecture

Two components in `components/`:

### `srne_modbus/` — RS485 Modbus RTU hub

- `class SrneModbus : public uart::UARTDevice, public Component`
- `MULTI_CONF = True` so multiple buses can coexist
- One in-flight request, FIFO queue of pending requests
- `send(address, function, start_register, num_registers, payload=nullptr)` enqueues
- Frame builder produces `[addr][fn][reg_hi][reg_lo][cnt_hi][cnt_lo][crc_lo][crc_hi]` for `0x03`, and the longer write framings for `0x06`/`0x10`
- RX parser determines expected frame length from `function`+`byte_count` (or 5 for error responses), validates CRC, then calls `on_modbus_data(buffer)` on every registered device — each device filters by its `address_`
- Response timeout: 1000 ms; on timeout the in-flight slot is cleared and the next queued request is sent
- Optional `flow_control_pin` (`GPIOPin*`) for RS485 DE/RE: driven high before `write_array`+`flush`, then low

V1 only enqueues `0x03` requests, but the framing/parsing supports `0x06` and `0x10` so adding writable entities later is additive.

Public surface:
```cpp
struct ModbusRequest {
  uint8_t address;
  uint8_t function;
  uint16_t start_register;
  uint16_t num_registers;
  std::vector<uint8_t> payload;  // for 0x06/0x10, empty for 0x03
};

class SrneModbusDevice {
 public:
  virtual void on_modbus_data(const std::vector<uint8_t> &data) = 0;
  uint8_t get_address() const { return address_; }
  // ...
};
```

### `srne_inverter/` — Device component

- `class SrneInverter : public PollingComponent, public srne_modbus::SrneModbusDevice`
- Default `address: 0x01`, default `update_interval: 10s`
- `update()` issues one polling step per call (state machine); the modbus hub queues them all and serialises on the wire
- `on_modbus_data()` checks address, error bit, then dispatches by `byte_count` (and the most-recently-sent block tag) to the right unpacker
- Online watchdog identical to `EG4Bms`: `no_response_count_` increments each `update()`, resets when a valid response for this address arrives; on threshold (5) `online_status` flips to false

## Polling state machine

Each block ≤ 32 registers. All run every poll cycle except product info, which runs at boot then every ~30 cycles.

| Step | Range | # regs | Bytes | Purpose |
|---|---|---|---|---|
| A | `0x0100`–`0x0111` | 18 | 36 | SOC, battery V/I, PV1 V/I/W, charge state, charge power, PV2 V/I/W |
| B | `0x0210`–`0x0224` | 21 | 42 | machine state, bus V, grid V/I/Hz, inverter V/I/Hz, load V/I/W/VA, batt charge I, load %, 3 heatsink temps, PV charge I |
| C | `0x0200`–`0x0207` | 8 | 16 | fault bits (4) + active fault codes (4) |
| D (slow) | `0x0014`–`0x0017` | 4 | 8 | software/hardware versions |
| E (slow) | `0x0035`–`0x0048` | 20 | 40 | Product SN string (low byte of each register is valid ASCII) |

A+B+C = 3 reads × ~50 ms-on-wire each → comfortably fits a 10 s update.

Block dispatch uses both the request step (set just before `send`) and the `byte_count` in the response. The step tag avoids any ambiguity if two blocks happen to have the same byte count.

## Entities

All entities are optional in YAML. None are required; users wire up only what they care about.

### `sensor`

| YAML key | Source | Unit | Scale | Notes |
|---|---|---|---|---|
| `battery_soc` | `0x0100` | % | ×1 | |
| `battery_voltage` | `0x0101` | V | ×0.1 | uint16 |
| `battery_current` | `0x0102` | A | ×0.1 | **int16, signed** (negative = discharge) |
| `pv1_voltage` | `0x0107` | V | ×0.1 | |
| `pv1_current` | `0x0108` | A | ×0.1 | |
| `pv1_power` | `0x0109` | W | ×1 | |
| `charge_power` | `0x010E` | W | ×1 | total (mains + PV) |
| `pv2_voltage` | `0x010F` | V | ×0.1 | |
| `pv2_current` | `0x0110` | A | ×0.1 | |
| `pv2_power` | `0x0111` | W | ×1 | |
| `pv_total_power` | derived | W | — | `pv1_power + pv2_power` (published only when both registers seen) |
| `bus_voltage` | `0x0212` | V | ×0.1 | |
| `grid_voltage` | `0x0213` | V | ×0.1 | phase A |
| `grid_current` | `0x0214` | A | ×0.1 | phase A |
| `grid_frequency` | `0x0215` | Hz | ×0.01 | |
| `inverter_voltage` | `0x0216` | V | ×0.1 | phase A output |
| `inverter_current` | `0x0217` | A | ×0.1 | phase A inductive |
| `inverter_frequency` | `0x0218` | Hz | ×0.01 | |
| `load_current` | `0x0219` | A | ×0.1 | |
| `load_active_power` | `0x021B` | W | ×1 | |
| `load_apparent_power` | `0x021C` | VA | ×1 | |
| `battery_charge_current` | `0x021E` | A | ×0.1 | mains side charge current |
| `load_percent` | `0x021F` | % | ×1 | |
| `heatsink_a_temperature` | `0x0220` | °C | ×0.1 | int16, DC-DC heat sink |
| `heatsink_b_temperature` | `0x0221` | °C | ×0.1 | int16, DC-AC heat sink |
| `heatsink_c_temperature` | `0x0222` | °C | ×0.1 | int16, transformer heat sink |
| `pv_charge_current` | `0x0224` | A | ×0.1 | battery charge current from PV |

### `binary_sensor`

| YAML key | Derivation |
|---|---|
| `online_status` | true when a valid response was received within the last 5 update cycles (same watchdog pattern as EG4) |
| `grid_present` | `grid_voltage > 50.0` (V). Cheap heuristic; avoids needing a separate enum. |
| `inverter_on` | `machine_state` is one of `5` (Inverter powered) or `7` (Mains→Inverter) |
| `fault` | any of `0x0200`–`0x0203` ≠ 0 |

### `text_sensor`

| YAML key | Source | Decoding |
|---|---|---|
| `machine_state` | `0x0210` | enum: 0 Power-up delay, 1 Waiting, 2 Initialization, 3 Soft start, 4 Mains powered, 5 Inverter powered, 6 Inverter→Mains, 7 Mains→Inverter, 8 Battery activate, 9 Shutdown by user, 10 Fault |
| `charge_state` | `0x010B` | enum: 0 Off, 1 Quick, 2 Const V, 3 Boost, 4 Float, 5 Reserved, 6 Li activate, 7 Reserved |
| `fault_codes` | `0x0204`–`0x0207` | non-zero codes joined with `;`, "None" if all zero. Code-to-text table is left as numeric IDs in V1 (PDF says fault meanings are in the instruction manual, which we don't have). |
| `software_version` | `0x0014`–`0x0015` | "CPU1 v%d.%02d / CPU2 v%d.%02d" |
| `hardware_version` | `0x0016`–`0x0017` | "Control v%d.%02d / Power v%d.%02d" |
| `serial_number` | `0x0035`–`0x0048` | concatenate low byte of each register as ASCII; trim trailing spaces/nulls |

## Out of scope for V1 (recorded for future PRs)

These are intentional cuts. Each is additive — none require breaking changes to the V1 entities.

- **Writable entities** (`switch`/`number`/`select`) — output priority, charge priority, output voltage/frequency, mains charge current limit, battery type, power on/off. All live in P03 (`0xDF00`–`0xDF0D`) and P05/P07 (`0xE000`–`0xE21B`). Framing supports `0x06`/`0x10`.
- **3-phase B/C registers** (`0x022A`–`0x0237`) — "specific machine models" only. Add a `three_phase: true` option when needed.
- **Historical statistics** (P08, `0xF000`–`0xF04B`) — last-7-days arrays, total running days, accumulated AH. Low value vs the always-current sensors; HA users typically derive these via Riemann sum.
- **Fault history** (P09, `0xF800`–`0xF8F0`) — 16 records × 16 registers each. Diagnostic-only, big read cost.
- **Password gating** (`E202`/`E203`) — needed only for write access to protected registers.

## Repository layout

```
esphome-srne-inverter/
├── components/
│   ├── srne_modbus/
│   │   ├── __init__.py
│   │   ├── srne_modbus.h
│   │   └── srne_modbus.cpp
│   └── srne_inverter/
│       ├── __init__.py
│       ├── srne_inverter.h
│       ├── srne_inverter.cpp
│       ├── sensor.py
│       ├── binary_sensor.py
│       └── text_sensor.py
├── docs/
│   └── superpowers/specs/2026-05-16-srne-inverter-design.md
├── esp32-example.yaml
├── README.md
├── REGISTER_MAP.md
├── WIRING.md
├── secrets.yaml.example
├── Solar_inverter_charger_communication_protocol.pdf      (V1.0, framing only)
└── srne-hybrid-solar-inverter-modbus-protocol-v1-7.pdf    (V1.7, framing + registers)
```

## Example YAML (target)

```yaml
external_components:
  - source: github://rar/esphome-srne-inverter@main
    refresh: 0s

uart:
  id: uart_0
  baud_rate: 9600
  tx_pin: GPIO16
  rx_pin: GPIO17
  rx_buffer_size: 256

srne_modbus:
  id: modbus0
  uart_id: uart_0
  # flow_control_pin: GPIO4   # optional, for RS485 DE/RE

srne_inverter:
  id: inv0
  srne_modbus_id: modbus0
  address: 0x01
  update_interval: 10s

sensor:
  - platform: srne_inverter
    srne_inverter_id: inv0
    battery_soc: { name: "Battery SOC" }
    battery_voltage: { name: "Battery V" }
    battery_current: { name: "Battery A" }
    pv1_power: { name: "PV1 Power" }
    pv2_power: { name: "PV2 Power" }
    pv_total_power: { name: "PV Total Power" }
    grid_voltage: { name: "Grid V" }
    inverter_voltage: { name: "Inverter V" }
    load_active_power: { name: "Load W" }
    load_percent: { name: "Load %" }

binary_sensor:
  - platform: srne_inverter
    srne_inverter_id: inv0
    online_status: { name: "Inverter Online" }
    grid_present: { name: "Grid Present" }
    inverter_on: { name: "Inverter On" }
    fault: { name: "Inverter Fault" }

text_sensor:
  - platform: srne_inverter
    srne_inverter_id: inv0
    machine_state: { name: "Inverter State" }
    charge_state: { name: "Charge State" }
    fault_codes: { name: "Fault Codes" }
    serial_number: { name: "Inverter SN" }
    software_version: { name: "Inverter FW" }
```

## Validation plan

- `esphome config esp32-example.yaml` must validate.
- `esphome compile esp32-example.yaml` for an ESP32 target must build clean (no warnings about unused includes).
- On real hardware: verify CRC by observing that the inverter responds (any response means our CRC matched), and that decoded values are plausible (battery V ~48 V for a 48 V system, grid Hz ~50/60 Hz, SOC 0-100). Fine-tuning of any scale errors happens against real captures.
