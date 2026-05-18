import esphome.codegen as cg
from esphome.components import select
import esphome.config_validation as cv
from esphome.const import CONF_ID, ENTITY_CATEGORY_CONFIG

from . import SRNE_INVERTER_COMPONENT_SCHEMA, CONF_SRNE_INVERTER_ID, srne_inverter_ns

DEPENDENCIES = ["srne_inverter"]

SrneSelect = srne_inverter_ns.class_("SrneSelect", select.Select, cg.Component)

CONF_OUTPUT_PRIORITY = "output_priority"
CONF_CHARGE_PRIORITY = "charge_priority"
CONF_BATTERY_TYPE = "battery_type"
CONF_AC_INPUT_VOLTAGE_RANGE = "ac_input_voltage_range"
CONF_PARALLEL_MODE = "parallel_mode"

# Order MUST match the inverter's enum values — index in this list is the raw
# value written to the register.
#   0xE204 Output priority: 0 solar, 1 line, 2 SBU
OUTPUT_PRIORITY_OPTIONS = ["Solar", "Line", "SBU"]
#   0xE20F Charge priority: 0 PV preferred, 1 Mains preferred, 2 Hybrid, 3 PV only
CHARGE_PRIORITY_OPTIONS = ["PV preferred", "Mains preferred", "Hybrid", "PV only"]
#   0xE004 Battery type, per §5.2 menu item 08 of the user manual.
#   Indices (confirmed against the Anenji keypad — keypad showed "L16" while
#   raw register value was 6):
#     0=User-defined, 1=Sealed lead-acid, 2=Flooded lead-acid, 3=Gel,
#     4=LFP L14, 5=LFP L15, 6=LFP L16,
#     7..12=reserved,
#     13=Ternary N13, 14=Ternary N14
#
#   NOTE: the Anenji 12KW firmware refuses writes to 0xE004 with Modbus error
#   0x0B (permission denied) — battery type is keypad-only on that hardware.
#   Use the `text_sensor.battery_type` read-only mirror instead. This select
#   option is still exposed for SRNE variants where the write IS accepted.
BATTERY_TYPE_OPTIONS = [
    "User-defined",       # 0
    "Sealed lead-acid",   # 1
    "Flooded lead-acid",  # 2
    "Gel",                # 3
    "LFP L14",            # 4
    "LFP L15",            # 5
    "LFP L16",            # 6
    "Reserved (7)",       # 7
    "Reserved (8)",       # 8
    "Reserved (9)",       # 9
    "Reserved (10)",      # 10
    "Reserved (11)",      # 11
    "Reserved (12)",      # 12
    "Ternary N13",        # 13
    "Ternary N14",        # 14
]

#   0xE20B AC input voltage range, per V1.7 PDF (and confirmed against the
#   Anenji keypad — keypad showed "UPS" while raw register value was 1):
#   0=APL (wide range, output 100/105V, 85-140V), 1=UPS (narrow, 120/110V, 90-140V)
AC_INPUT_VOLTAGE_RANGE_OPTIONS = ["APL", "UPS"]

#   0xE201 Parallel mode, per §5.2 menu item 31:
#   0=SIG single inverter, 1=PAL parallel, 2/3/4=two-phase P0/P1/P2,
#   5/6/7=three-phase P1/P2/P3
PARALLEL_MODE_OPTIONS = [
    "SIG (single)",          # 0
    "PAL (parallel)",        # 1
    "2P0 (two-phase P0)",    # 2
    "2P1 (two-phase P1)",    # 3
    "2P2 (two-phase P2)",    # 4
    "3P1 (three-phase P1)",  # 5
    "3P2 (three-phase P2)",  # 6
    "3P3 (three-phase P3)",  # 7
]

# Register addresses (kept in sync with srne_inverter.cpp REG_* constants)
REG_OUTPUT_PRIORITY = 0xE204
REG_CHARGE_PRIORITY = 0xE20F
REG_BATTERY_TYPE = 0xE004
REG_AC_INPUT_VOLTAGE_RANGE = 0xE20B
REG_PARALLEL_MODE = 0xE201

CONFIG_SCHEMA = SRNE_INVERTER_COMPONENT_SCHEMA.extend(
    {
        cv.Optional(CONF_OUTPUT_PRIORITY): select.select_schema(
            SrneSelect,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:transmission-tower-export",
        ),
        cv.Optional(CONF_CHARGE_PRIORITY): select.select_schema(
            SrneSelect,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:solar-power",
        ),
        cv.Optional(CONF_BATTERY_TYPE): select.select_schema(
            SrneSelect,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:car-battery",
        ),
        cv.Optional(CONF_AC_INPUT_VOLTAGE_RANGE): select.select_schema(
            SrneSelect,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:sine-wave",
        ),
        cv.Optional(CONF_PARALLEL_MODE): select.select_schema(
            SrneSelect,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon="mdi:connection",
        ),
    }
)


async def _make_select(config, options, register_addr, hub):
    var = await select.new_select(config, options=options)
    await cg.register_component(var, config)
    cg.add(var.set_parent(hub))
    cg.add(var.set_register(register_addr))
    return var


async def to_code(config):
    hub = await cg.get_variable(config[CONF_SRNE_INVERTER_ID])

    if CONF_OUTPUT_PRIORITY in config:
        sel = await _make_select(
            config[CONF_OUTPUT_PRIORITY], OUTPUT_PRIORITY_OPTIONS, REG_OUTPUT_PRIORITY, hub
        )
        cg.add(hub.set_output_priority_select(sel))

    if CONF_CHARGE_PRIORITY in config:
        sel = await _make_select(
            config[CONF_CHARGE_PRIORITY], CHARGE_PRIORITY_OPTIONS, REG_CHARGE_PRIORITY, hub
        )
        cg.add(hub.set_charge_priority_select(sel))

    if CONF_BATTERY_TYPE in config:
        sel = await _make_select(
            config[CONF_BATTERY_TYPE], BATTERY_TYPE_OPTIONS, REG_BATTERY_TYPE, hub
        )
        cg.add(hub.set_battery_type_select(sel))

    if CONF_AC_INPUT_VOLTAGE_RANGE in config:
        sel = await _make_select(
            config[CONF_AC_INPUT_VOLTAGE_RANGE], AC_INPUT_VOLTAGE_RANGE_OPTIONS,
            REG_AC_INPUT_VOLTAGE_RANGE, hub
        )
        cg.add(hub.set_ac_input_voltage_range_select(sel))

    if CONF_PARALLEL_MODE in config:
        sel = await _make_select(
            config[CONF_PARALLEL_MODE], PARALLEL_MODE_OPTIONS, REG_PARALLEL_MODE, hub
        )
        cg.add(hub.set_parallel_mode_select(sel))
