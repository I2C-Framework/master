import click
import os
import math
import time
from smbus2 import SMBus, i2c_msg

MAGIC_NUMBER = 0x42
FIRMWARE_REGISTER = 0xA0
RANGE_MIN = 0x10
RANGE_MAX = 0x78
GROUP_REGISTER = 0xA5
SENSORS_TYPE_REGISTER = 0xA6

# Function to send message vy i2c
def send_message(bus, address, register, length):
    msg = i2c_msg.write(address, [register])
    bus.i2c_rdwr(msg)
    msg = i2c_msg.read(address, length)
    bus.i2c_rdwr(msg)
    data = 0
    #for i, b in enumerate(msg.buf):
    for i in range(0, length):
        data += int.from_bytes(msg.buf[i], byteorder='big') << (8*i)
    return data

def validate_hex(ctx, param, value):
    try:
        address = int(value[2:], 16)
        return address
    except (ValueError):
        raise click.BadParameter(f'{value} is not a valid hexadecimal number.')
    except (TypeError):
        return None
    
def send_firmware(bus, slave_address, firmware_content, file_size, restart_firmware):
    if(restart_firmware):
        msg = i2c_msg.write(slave_address, [FIRMWARE_REGISTER])
        bus.i2c_rdwr(msg)
        time.sleep(2)

    # Send file as part of 1024 byte chunks
    for i in range(0, file_size, 1024):
        chunk = []
        if i + 1024 > file_size:
            chunk = firmware_content[i:]
        else:
            chunk = firmware_content[i:i+1024]

        click.echo("Chunk number: " + str(i//1024+1) + " of " + str(math.ceil(file_size/1024)))
        # Message format: [register, block number, number of blocks in file, data]
        msg = i2c_msg.write(slave_address, [i//1024+1, math.ceil(file_size/1024)] + list(chunk))
        bus.i2c_rdwr(msg)
        
    click.echo("Firmware sent successfully")


@click.command()
@click.option('-b', '--bus', 'bus_number', default=1, prompt='I2C bus number',
              help='The I2C bus number to be used.', type=int)
@click.option('-f', '--firmware', 'firmware_path', prompt='Firmware path',
              help='The path to the firmware file to be sent.', type=str)
@click.option('-a', '--address', 'slave_address',
              help='The address of the I2C slave to be updated as hex (0x--).', callback=validate_hex, type=str)
@click.option('-r', '--restart', 'restart_firmware',
              help='Restart the firmware to go into bootloader mode for update.', is_flag=True)
@click.option('-g', '--group', 'device_group',
              help='The group of the device to be updated.', type=int)
@click.option('-s', '--sensors', 'sensors_type',
              help='The type of sensors of the device to be updated.', type=int)

def update_firmware(bus_number, firmware_path, slave_address, device_group, sensors_type, restart_firmware):
    """ Program to update the firmware of a microcontroller belonging to the I2C ecosystem """  
    count = sum([1 for arg in [slave_address, device_group, sensors_type] if arg is not None])
    if count != 1:
        raise click.UsageError('One and only one of the following arguments must be provided: --address, --group, --sensors')

    with SMBus(bus_number) as bus:
        file_size = os.path.getsize(firmware_path)
        firmware = open(firmware_path, "rb")
        firmware_content = bytearray(firmware.read())

        if len(firmware_content) != file_size:
            click.echo("Error: file size does not match")
            return
        
        if slave_address is not None:
            send_firmware(bus, slave_address, firmware_content, file_size, restart_firmware)
        elif device_group is not None:
            # Detect all devices
            for i in range(RANGE_MIN, RANGE_MAX):
                # Write ID register
                msg = i2c_msg.read(i, 1)
                # Send message
                try:
                    bus.i2c_rdwr(msg)
                except:
                    continue

                if(int.from_bytes(msg.buf[0], byteorder='little') == MAGIC_NUMBER):
                    group = send_message(bus, i, GROUP_REGISTER, 1)
                    if(group == device_group):
                        # Send firmware
                        click.echo("Updating device with address: " + hex(i))
                        send_firmware(bus, i, firmware_content, file_size, restart_firmware)
        elif sensors_type is not None:
            # Detect all devices
            for i in range(RANGE_MIN, RANGE_MAX):
                # Write ID register
                msg = i2c_msg.read(i, 1)
                # Send message
                try:
                    bus.i2c_rdwr(msg)
                except:
                    continue

                if(int.from_bytes(msg.buf[0], byteorder='little') == MAGIC_NUMBER):
                    group = send_message(bus, i, SENSORS_TYPE_REGISTER, 1)
                    if(group == device_group):
                        # Send firmware
                        click.echo("Updating device with address: " + hex(i))
                        send_firmware(bus, i, firmware_content, file_size, restart_firmware) 
            
        

if __name__ == '__main__':
    update_firmware()