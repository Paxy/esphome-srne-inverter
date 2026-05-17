import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.components import uart
from esphome.const import CONF_FLOW_CONTROL_PIN, CONF_ID

CODEOWNERS = ["@rar"]
DEPENDENCIES = ["uart"]
MULTI_CONF = True

CONF_SRNE_MODBUS_ID = "srne_modbus_id"

srne_modbus_ns = cg.esphome_ns.namespace("srne_modbus")
SrneModbus = srne_modbus_ns.class_("SrneModbus", cg.Component, uart.UARTDevice)
SrneModbusDevice = srne_modbus_ns.class_("SrneModbusDevice")

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(SrneModbus),
            cv.Optional(CONF_FLOW_CONTROL_PIN): pins.gpio_output_pin_schema,
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
    .extend(uart.UART_DEVICE_SCHEMA)
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    if CONF_FLOW_CONTROL_PIN in config:
        pin = await cg.gpio_pin_expression(config[CONF_FLOW_CONTROL_PIN])
        cg.add(var.set_flow_control_pin(pin))


def srne_modbus_device_schema(default_address):
    schema = {
        cv.GenerateID(CONF_SRNE_MODBUS_ID): cv.use_id(SrneModbus),
        cv.Optional("address", default=default_address): cv.hex_uint8_t,
    }
    return cv.Schema(schema)


async def register_srne_modbus_device(var, config):
    parent = await cg.get_variable(config[CONF_SRNE_MODBUS_ID])
    cg.add(var.set_parent(parent))
    cg.add(var.set_address(config["address"]))
    cg.add(parent.register_device(var))
