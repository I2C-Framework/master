import click
from smbus2 import SMBus, i2c_msg
import time

MAGIC_NUMBER = 0x42
RANGE_MIN = 0x10
RANGE_MAX = 0x78

ID_REGISTER = 0xA1
MAJOR_VERSION_REGISTER = 0xA2
MINOR_VERSION_REGISTER = 0xA3
FIX_VERSION_REGISTER = 0xA4
GROUP_REGISTER = 0xA5
SENSORS_TYPE_REGISTER = 0xA6
NAME_REGISTER = 0xA7

def get_string_register(bus, address, register, length):
    write = i2c_msg.write(address, [register])
    read = i2c_msg.read(address, length)
    bus.i2c_rdwr(write, read)
    bytes_data = list(read)
    response_text = "".join(chr(byte) for byte in bytes_data)
    return response_text
    

# Function to send message i2c
def get_int_register(bus, address, register, length):
    write = i2c_msg.write(address, [register])
    read = i2c_msg.read(address, length)
    bus.i2c_rdwr(write, read)
    data = 0
    for i in range(0, length):
        data += int.from_bytes(read.buf[i], byteorder='big') << (8*i)
    return data

@click.command()
@click.option('-b', '--bus', 'bus_number', default=1, prompt='I2C bus number', help='The I2C bus number to be used.', type=int)

def detect(bus_number):
    """ Program to detect all I2C devices belonging to the I2C ecosystem """    
    bus = SMBus(bus_number)    

    print("#  uuid        i2c      firmware   group  type            name")
    print("----------------------------------------------------------------")
    counter = 0

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
            id = get_int_register(bus, i, ID_REGISTER, 4)
            major_version = get_int_register(bus, i, MAJOR_VERSION_REGISTER, 1)
            minor_version = get_int_register(bus, i, MINOR_VERSION_REGISTER, 1)
            fix_version = get_int_register(bus, i, FIX_VERSION_REGISTER, 1)
            group = get_int_register(bus, i, GROUP_REGISTER, 1)
            sensors_type = get_string_register(bus, i, SENSORS_TYPE_REGISTER, 32)
            name = get_string_register(bus, i, NAME_REGISTER, 32)
            
            counter += 1
            
            print(str(counter) + ". " + hex(id) + "    " + hex(i) + "     " + str(major_version) + "." + str(minor_version) + "." + str(fix_version) + "      " + str(group) + "      " + sensors_type + "    " + name)

if __name__ == '__main__':
    detect()