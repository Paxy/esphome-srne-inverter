import esphome.codegen as cg
from esphome.components import sensor
import esphome.config_validation as cv
from esphome.const import (
    CONF_CURRENT,
    CONF_FREQUENCY,
    CONF_POWER,
    CONF_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_FREQUENCY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    STATE_CLASS_MEASUREMENT,
    UNIT_AMPERE,
    UNIT_CELSIUS,
    UNIT_HERTZ,
    UNIT_PERCENT,
    UNIT_VOLT,
    UNIT_WATT,
)

from . import SRNE_INVERTER_COMPONENT_SCHEMA, CONF_SRNE_INVERTER_ID

DEPENDENCIES = ["srne_inverter"]

# Block A (controller / PV)
CONF_BATTERY_SOC = "battery_soc"
CONF_BATTERY_VOLTAGE = "battery_voltage"
CONF_BATTERY_CURRENT = "battery_current"
CONF_PV1_VOLTAGE = "pv1_voltage"
CONF_PV1_CURRENT = "pv1_current"
CONF_PV1_POWER = "pv1_power"
CONF_PV2_VOLTAGE = "pv2_voltage"
CONF_PV2_CURRENT = "pv2_current"
CONF_PV2_POWER = "pv2_power"
CONF_PV_TOTAL_POWER = "pv_total_power"
CONF_CHARGE_POWER = "charge_power"

UNIT_VOLT_AMPS = "VA"

VOLTAGE_SCHEMA = sensor.sensor_schema(
    unit_of_measurement=UNIT_VOLT,
    accuracy_decimals=1,
    device_class=DEVICE_CLASS_VOLTAGE,
    state_class=STATE_CLASS_MEASUREMENT,
)
CURRENT_SCHEMA = sensor.sensor_schema(
    unit_of_measurement=UNIT_AMPERE,
    accuracy_decimals=1,
    device_class=DEVICE_CLASS_CURRENT,
    state_class=STATE_CLASS_MEASUREMENT,
)
POWER_SCHEMA = sensor.sensor_schema(
    unit_of_measurement=UNIT_WATT,
    accuracy_decimals=0,
    device_class=DEVICE_CLASS_POWER,
    state_class=STATE_CLASS_MEASUREMENT,
)
PERCENT_SCHEMA = sensor.sensor_schema(
    unit_of_measurement=UNIT_PERCENT,
    accuracy_decimals=0,
    state_class=STATE_CLASS_MEASUREMENT,
)

CONFIG_SCHEMA = SRNE_INVERTER_COMPONENT_SCHEMA.extend(
    {
        cv.Optional(CONF_BATTERY_SOC): PERCENT_SCHEMA,
        cv.Optional(CONF_BATTERY_VOLTAGE): VOLTAGE_SCHEMA,
        cv.Optional(CONF_BATTERY_CURRENT): CURRENT_SCHEMA,
        cv.Optional(CONF_PV1_VOLTAGE): VOLTAGE_SCHEMA,
        cv.Optional(CONF_PV1_CURRENT): CURRENT_SCHEMA,
        cv.Optional(CONF_PV1_POWER): POWER_SCHEMA,
        cv.Optional(CONF_PV2_VOLTAGE): VOLTAGE_SCHEMA,
        cv.Optional(CONF_PV2_CURRENT): CURRENT_SCHEMA,
        cv.Optional(CONF_PV2_POWER): POWER_SCHEMA,
        cv.Optional(CONF_PV_TOTAL_POWER): POWER_SCHEMA,
        cv.Optional(CONF_CHARGE_POWER): POWER_SCHEMA,
    }
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_SRNE_INVERTER_ID])

    mapping = {
        CONF_BATTERY_SOC: hub.set_battery_soc_sensor,
        CONF_BATTERY_VOLTAGE: hub.set_battery_voltage_sensor,
        CONF_BATTERY_CURRENT: hub.set_battery_current_sensor,
        CONF_PV1_VOLTAGE: hub.set_pv1_voltage_sensor,
        CONF_PV1_CURRENT: hub.set_pv1_current_sensor,
        CONF_PV1_POWER: hub.set_pv1_power_sensor,
        CONF_PV2_VOLTAGE: hub.set_pv2_voltage_sensor,
        CONF_PV2_CURRENT: hub.set_pv2_current_sensor,
        CONF_PV2_POWER: hub.set_pv2_power_sensor,
        CONF_PV_TOTAL_POWER: hub.set_pv_total_power_sensor,
        CONF_CHARGE_POWER: hub.set_charge_power_sensor,
    }
    for key, setter in mapping.items():
        if key in config:
            sens = await sensor.new_sensor(config[key])
            cg.add(setter(sens))
