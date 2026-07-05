# SRNE HSI-1500S — Modbus Register Map & Documentation

**Model:** SRNE HSI-1500S (1.5KW, 12V, Single Phase, Single MPPT)  
**Battery:** 12V LFP (4S, nominal 12.8V)  
**Protocol:** Modbus RTU, 9600 8N1, slave address 0x01

---

## Modbus Scan Summary

Two scans were performed (12:49 and 12:57, July 5 2026).  
**274 out of 353 registers responded**, 79 return ERROR 0x02 (illegal address).

### Key differences between scans

| Register | Scan 1 | Scan 2 | Conclusion |
|----------|--------|--------|------------|
| 0x0100 SOC | 0% | **100%** | Battery connected between scans ★ |
| 0x0101 Battery V | 0.0V | **13.3V** | 12V LFP battery confirmed ★ |
| 0x0107 PV V | 13.7V | 13.8V | PV issue (panels not producing) |
| 0x020E | 12573 | 14394 | Unknown — changes over time |
| 0x021B Load W | 227 | 263 | Normal load variation |
| 0x021C Load VA | 282 | 306 | Normal load variation |
| 0x021F Load % | 18 | 20 | Normal load variation |

---

## Register Map

### Page 0x00 — System Info (0x0045-0x0049)

| Address | Scan value | Type | Description |
|---------|-----------|------|-------------|
| 0x0045 | 48 | ASCII '0' | Part of serial number / version string |
| 0x0046 | 48 | ASCII '0' | |
| 0x0047 | 50 | ASCII '2' | |
| 0x0048 | 55 | ASCII '7' | |
| 0x0049 | 0 | — | |

> The RAR component reads these registers for software/hardware version
> and serial number. Format is ASCII, read in blocks.

---

### Page 0x01 — PV / Battery (0x0100-0x010F)

| Address | Type | Multiplier | Description | Scan 2 | Real value |
|---------|------|------------|-------------|--------|------------|
| 0x0100 | u16 | ×1 % | Battery SOC | 100 | **100%** |
| 0x0101 | u16 | ×0.1 V | Battery Voltage | 133 | **13.3V** |
| 0x0102 | i16 | ×0.1 A | Battery Current (signed) | 0 | 0.0A |
| 0x0103 | i16 | ×0.1 A | Battery Current (mirror?) | 0 | 0.0A |
| 0x0104 | u16 | ? | Unknown | 0 | — |
| 0x0105 | u16 | ? | Unknown | 0 | — |
| 0x0106 | u16 | ? | Unknown | 0 | — |
| 0x0107 | u16 | ×0.1 V | PV1 Voltage | 138 | **13.8V** |
| 0x0108 | u16 | ×0.1 A | PV1 Current | 0 | 0.0A |
| 0x0109 | u16 | ×1 W | PV1 Power | 0 | 0W |
| 0x010A | u16 | ? | Unknown | 0 | — |
| 0x010B | u16 | enum | Charge State | 0 | — |
| 0x010C | u16 | ? | Unknown | 0 | — |
| 0x010D | u16 | ? | Unknown | 0 | — |
| 0x010E | u16 | ×1 W | Charge Power (total) | 0 | 0W |
| 0x010F | — | — | **Does not exist** (PV2 on larger models) | ERROR | — |

> **IMPORTANT:** 0x0110+ return ERROR 0x02 — HSI-1500S has no PV2 or
> extended PV registers. Only 0x0100-0x010F exist.

---

### Page 0x02 — Inverter / Grid / Load (0x0200-0x0227)

| Address | Type | Multiplier | Description | Scan 2 | Real value |
|---------|------|------------|-------------|--------|------------|
| 0x0200-0x020B | bitmask | — | Fault bits [0-11] | 0 | No faults ✓ |
| 0x020C | u16 | ? | Unknown (0x1A07) | 6663 | — |
| 0x020D | u16 | ? | Unknown (0x050C) | 1292 | — |
| 0x020E | u16 | ? | Unknown (changes) | 14394 | — |
| 0x020F | u16 | ? | Unknown | 0 | — |
| 0x0210 | u16 | enum | **Machine State** | 4 | Standby/Bypass |
| 0x0211 | u16 | bool | Password Protection | 0 | Off |
| 0x0212 | u16 | ×0.1 V | **Bus Voltage** | 4166 | **416.6V** |
| 0x0213 | u16 | ×0.1 V | **Grid Voltage** | 2355 | **235.5V** |
| 0x0214 | u16 | ×0.1 A | **Grid Current** | 12 | **1.2A** |
| 0x0215 | u16 | ×0.01 Hz | **Grid Frequency** | 4999 | **49.99Hz** |
| 0x0216 | u16 | ×0.1 V | **Inverter Voltage** | 2350 | **235.0V** |
| 0x0217 | u16 | ×0.1 A | **Inverter Current** | 0 | 0.0A |
| 0x0218 | u16 | ×0.01 Hz | **Inverter Frequency** | 4999 | **49.99Hz** |
| 0x0219 | u16 | ×0.1 A | **Load Current** | 12 | **1.2A** |
| 0x021A | u16 | ? | Unknown | 0 | — |
| 0x021B | u16 | ×1 W | **Load Active Power** | 263 | **263W** |
| 0x021C | u16 | ×1 VA | **Load Apparent Power** | 306 | **306VA** |
| 0x021D | u16 | ? | Unknown | 0 | — |
| 0x021E | u16 | ×0.1 A | Battery Charge (mains) | 0 | 0.0A |
| 0x021F | u16 | ×1 % | **Load Percent** | 20 | **20%** |
| 0x0220 | i16 | ×0.1 °C | **Heatsink A Temp** | 297 | **29.7°C** |
| 0x0221 | i16 | ×0.1 °C | **Heatsink B Temp** | 328 | **32.8°C** |
| 0x0222 | i16 | ×0.1 °C | **Heatsink C Temp** | 393 | **39.3°C** |
| 0x0223 | u16 | ? | Unknown | 0 | — |
| 0x0224 | u16 | ×0.1 A | PV Charge Current | 0 | 0.0A |
| 0x0225 | u16 | ? | Unknown | 22 | — |
| 0x0226 | u16 | ? | Unknown | 0 | — |
| 0x0227 | u16 | ? | Unknown | 0 | — |

> **IMPORTANT:** 0x0228+ return ERROR 0x02 — HSI-1500S is **single phase**.
> No L2, no DC bus +/-, no split-phase support.

---

### Page 0xE0 — Battery Settings (0xE000-0xE039)

| Address | Type | Description | Current value | Comment |
|---------|------|-------------|---------------|---------|
| 0xE000 | u16 | ? | 0 | |
| 0xE001 | u16 | Max Charge Voltage (0.1V) | 600 (60.0V) | ⚠️ For 48V? verify |
| 0xE002 | u16 | Battery Capacity (Ah) | 100 | 100Ah |
| 0xE003 | u16 | ? | 12 | |
| 0xE004 | u16 | Battery Type | 15 | LFP? |
| 0xE005 | u16 | Battery Voltage (0.1V) | 155 (15.5V) | Current voltage? |
| 0xE006-0xE00E | u16 | Battery Voltage Thresholds | 144→112 | Descending thresholds |
| **0xE00F** | u16 | **SOC Discharge Cutoff** | **5** | **5%** |
| 0xE010 | u16 | ? | 30 | |
| 0xE011 | u16 | ? | 5 | |
| 0xE012 | u16 | ? | 120 (12.0V?) | |
| 0xE013-0xE014 | u16 | ? | 5, 5 | |
| 0xE015 | u16 | ? | 60 | |
| 0xE016 | i16 | ? | -30 (0xFFE2) | |
| 0xE017 | u16 | ? | 60 | |
| 0xE018 | i16 | ? | -30 (0xFFE2) | |
| 0xE019-0xE01C | u16 | ? | 0, 5, 120, 0 | |
| **0xE01D** | u16 | **SOC Charge Cutoff** | **100** | **100%** |
| **0xE01E** | u16 | **SOC Discharge Alarm** | **15** | **15%** |
| **0xE01F** | u16 | **SOC Switch to Mains** | **10** | **10%** |
| **0xE020** | u16 | SOC Switch to Inverter | 100 | 100% |
| 0xE021-0xE025 | u16 | ? | 0, 137, 10, 25, 1 | |

---

### Page 0xE2 — Inverter Settings (0xE200-0xE21B)

| Address | Type | Description | Current value | Comment |
|---------|------|-------------|---------------|---------|
| 0xE200 | u16 | ? | 1 | |
| 0xE201 | u16 | ? | 96 | |
| 0xE202-0xE203 | u16 | ? | 0, 0 | |
| **0xE204** | enum | **Output Priority** | **1** | **Solar First** |
| **0xE205** | u16 | **Mains Charge Current** (0.1A) | **600** | **60.0A** |
| 0xE206-0xE207 | u16 | ? | 0, 0 | |
| **0xE208** | u16 | **Output Voltage** (0.1V) | **2300** | **230.0V** |
| 0xE209 | u16 | Output Frequency (0.01Hz) | 5000 | 50.00Hz |
| **0xE20A** | u16 | **Max Charge Current** (0.1A) | **200** | **20.0A** |
| **0xE20B** | enum | **AC Input Voltage Range** | **1** | **UPS mode** |
| 0xE20C | bool | Eco Mode | 0 | Off |
| **0xE20D** | bool | **Overload Auto Restart** | **1** | **On** |
| **0xE20E** | bool | **Overheat Auto Restart** | **1** | **On** |
| **0xE20F** | enum | **Charge Priority** | **2** | |
| **0xE210** | bool | **Buzzer Alarm** | **1** | **On** |
| 0xE211-0xE21A | u16 | ? | 1, 1, 1, 0, 0, 0, 12, 0, 0, 0 | |
| 0xE21B | u16 | ? | 7 | |

---

### Page 0xF0 — NEW PAGE (0xF000-0xF04D)

This page **does not exist** in the original RAR/esphome-srne-inverter project.
Found exclusively on the HSI-1500S model. Content is partially unknown.

| Address | Type | Value | Possible meaning |
|---------|------|-------|------------------|
| 0xF000-0xF006 | u16 | 0 | Zeros |
| 0xF007 | u16 | 2 | Unknown |
| 0xF008 | u16 | 91 | Unknown (0x5B = '[') |
| 0xF00F | u16 | 5 | Mirrors 0xE00F? (SOC cutoff) |
| 0xF015-0xF016 | u16 | 2, 91 | Mirrors 0xF007-0xF008 |
| 0xF01C-0xF01D | u16 | 15, 27 | Unknown |
| 0xF023-0xF024 | u16 | 15, 26 | Unknown (near 0xF01C) |
| **0xF02A** | u16 | **6663** | ⚠️ Same as 0x020C! |
| 0xF02B | u16 | 1280 | Unknown |
| 0xF030 | u16 | 17 | Unknown |
| 0xF034 | u16 | 93 | Unknown |
| 0xF03A | u16 | 59 | Unknown |
| 0xF03D | u16 | 17 | Unknown |
| 0xF03F | u16 | 13 | Unknown |
| 0xF040-0xF042 | u16 | 6663, 1038, 6182 | Unknown (triplet?) |
| 0xF043-0xF045 | u16 | 6663, 1038, 6182 | Repeated! |
| 0xF046 | u16 | 93 | |
| 0xF048 | u16 | 58 | |
| 0xF04B | u16 | 43 | |

> This page is likely factory/diagnostic data or a configuration backup.
> Unknown whether values change during operation. Needs further research.

---

## What doesn't work on HSI-1500S (vs original RAR YAML)

| Feature | Register | Status | Reason |
|---------|----------|--------|--------|
| PV2 Voltage | 0x010F+ | ❌ ERROR | Single MPPT |
| PV2 Current | 0x0110+ | ❌ ERROR | Single MPPT |
| PV2 Power | 0x0111+ | ❌ ERROR | Single MPPT |
| DC Bus + | 0x0228 | ❌ ERROR | No split-phase |
| DC Bus - | 0x0229 | ❌ ERROR | No split-phase |
| Grid Voltage L2 | 0x022A | ❌ ERROR | Single phase |
| Inverter Voltage L2 | 0x022C | ❌ ERROR | Single phase |
| Inverter Current L2 | 0x022E | ❌ ERROR | Single phase |
| Load Current L2 | 0x0230 | ❌ ERROR | Single phase |
| Load Power L2 | 0x0232 | ❌ ERROR | Single phase |
| Load Apparent Power L2 | 0x0234 | ❌ ERROR | Single phase |
| Load Percent L2 | 0x0236 | ❌ ERROR | Single phase |
| Parallel Mode | 0xE201? | ⚠️ | May exist but different |

---

## Machine State enum (0x0210)

| Value | Meaning |
|-------|---------|
| 4 | **Standby/Bypass** (current) |
| ? | Need more samples in different states |

## Output Priority enum (0xE204)

| Value | Meaning |
|-------|---------|
| 1 | **Solar First** (current) |
| 2 | Solar + Utility (SBU?) |

## AC Input Voltage Range enum (0xE20B)

| Value | Meaning |
|-------|---------|
| 1 | **UPS** (narrow range, 184-253V) |
| 2 | APL (wide range, 170-280V) |

---

## 12V LFP Battery Notes

- **Nominal voltage:** 12.8V (4S × 3.2V)
- **Charge voltage:** 14.4-14.6V (4S × 3.6-3.65V)
- **Discharge cutoff:** 10.0V (4S × 2.5V)
- **Float:** 13.5-13.6V
- Current reading: **13.3V** = ~100% SOC (without BMS, approximate)

> Without CAM/BMS communication, the inverter can only approximate SOC
> based on voltage. For accurate SOC, connect BMS via CAM bus.

---

## Files

| File | Description |
|------|-------------|
| `srne-hsi1500s.yaml` | **Final ESPHome YAML** — flash to ESP32 |
| `srne-hsi1500s-scan.yaml` | Scanner firmware (temporary) |
| `srne-hsi1500s-scan-logs.txt` | Log from second scan |
| `SRNE_HSI1500S_REGISTER_MAP.md` | This file — register map |
| `parse_scan.py` | Python parser for scan logs |
| `scan_diff.py` | Tool for comparing two scans |
| `README_SCAN.md` | Scanning instructions |
