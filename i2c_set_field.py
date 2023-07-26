import click
from smbus2 import SMBus, i2c_msg
import time

GROUP_REGISTER = 0xA3
SENSORS_TYPE_REGISTER = 0xA4
NAME_REGISTER = 0xA5

def validate_hex(ctx, param, value):
    try:
        address = int(value[2:], 16)
        return address
    except (ValueError):
        raise click.BadParameter(f'{value} is not a valid hexadecimal number.')
    except (TypeError):
        return None

def set_value(bus, address, register, value):
    msg = i2c_msg.write(address, [register] + value)
    bus.i2c_rdwr(msg)

@click.command()
@click.option('-b', '--bus', 'bus_number', default=1, prompt='I2C bus number', help='The I2C bus number to be used.', type=int)
@click.option('-a', '--address', 'slave_address', help='The address of the I2C slave to be updated as hex (0x--).', callback=validate_hex, type=str)
@click.option('-f', '--field', 'field', prompt='Field to be set', help='The field to be set.', type=click.Choice(['group', 'type', 'name'], case_sensitive=False))
@click.option('-v', '--value', 'value', prompt='Value to be set', help='The value to be set.', type=str)

def set_field(bus_number, slave_address, field, value):
    bus = SMBus(bus_number)
    if(field == "group"):
        int_value = int(value)
        set_value(bus, slave_address, GROUP_REGISTER, [int_value])
    elif(field == "type"):
        type_byte_array = [ord(c) for c in value]
        set_value(bus, slave_address, SENSORS_TYPE_REGISTER, type_byte_array)
    elif(field == "name"):
        name_byte_array = [ord(c) for c in value]
        set_value(bus, slave_address, NAME_REGISTER, name_byte_array)
    else:
        print("Field not found")
    
if __name__ == '__main__':
    set_field()