import esphome.codegen as cg
from esphome.components import switch
import esphome.config_validation as cv
from esphome.const import CONF_ID, ENTITY_CATEGORY_CONFIG

from . import SRNE_INVERTER_COMPONENT_SCHEMA, CONF_SRNE_INVERTER_ID, srne_inverter_ns

DEPENDENCIES = ["srne_inverter"]

SrneSwitch = srne_inverter_ns.class_("SrneSwitch", switch.Switch, cg.Component)

CONF_ECO_MODE = "eco_mode"
CONF_OVERLOAD_AUTO_RESTART = "overload_auto_restart"
CONF_OVERHEAT_AUTO_RESTART = "overheat_auto_restart"
CONF_BUZZER_ALARM = "buzzer_alarm"
CONF_INVERTER_TO_BYPASS = "inverter_to_bypass"

REG_ECO_MODE = 0xE20C
REG_OVERLOAD_AUTO_RESTART = 0xE20D
REG_OVERHEAT_AUTO_RESTART = 0xE20E
REG_BUZZER_ALARM = 0xE210
REG_INVERTER_TO_BYPASS = 0xE212

CONFIG_SCHEMA = SRNE_INVERTER_COMPONENT_SCHEMA.extend(
    {
        cv.Optional(CONF_ECO_MODE): switch.switch_schema(
            SrneSwitch,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:leaf",
        ),
        cv.Optional(CONF_OVERLOAD_AUTO_RESTART): switch.switch_schema(
            SrneSwitch,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:restart-alert",
        ),
        cv.Optional(CONF_OVERHEAT_AUTO_RESTART): switch.switch_schema(
            SrneSwitch,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:thermometer-alert",
        ),
        cv.Optional(CONF_BUZZER_ALARM): switch.switch_schema(
            SrneSwitch,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:bullhorn",
        ),
        cv.Optional(CONF_INVERTER_TO_BYPASS): switch.switch_schema(
            SrneSwitch,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:transit-connection-variant",
        ),
    }
)


async def _make_switch(config, register_addr, hub, setter):
    s = await switch.new_switch(config)
    await cg.register_component(s, config)
    cg.add(s.set_parent(hub))
    cg.add(s.set_register(register_addr))
    cg.add(setter(s))


async def to_code(config):
    hub = await cg.get_variable(config[CONF_SRNE_INVERTER_ID])

    if CONF_ECO_MODE in config:
        await _make_switch(config[CONF_ECO_MODE], REG_ECO_MODE, hub, hub.set_eco_mode_switch)

    if CONF_OVERLOAD_AUTO_RESTART in config:
        await _make_switch(config[CONF_OVERLOAD_AUTO_RESTART], REG_OVERLOAD_AUTO_RESTART, hub,
                           hub.set_overload_auto_restart_switch)

    if CONF_OVERHEAT_AUTO_RESTART in config:
        await _make_switch(config[CONF_OVERHEAT_AUTO_RESTART], REG_OVERHEAT_AUTO_RESTART, hub,
                           hub.set_overheat_auto_restart_switch)

    if CONF_BUZZER_ALARM in config:
        await _make_switch(config[CONF_BUZZER_ALARM], REG_BUZZER_ALARM, hub,
                           hub.set_buzzer_alarm_switch)

    if CONF_INVERTER_TO_BYPASS in config:
        await _make_switch(config[CONF_INVERTER_TO_BYPASS], REG_INVERTER_TO_BYPASS, hub,
                           hub.set_inverter_to_bypass_switch)
