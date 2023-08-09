import click
from smbus2 import SMBus, i2c_msg
import time

MAGIC_NUMBER = 0x42
RANGE_MIN = 0x10
RANGE_MAX = 0x78

ID_REGISTER = 0xA1
VERSION_HASH_REGISTER = 0xA2
GROUP_REGISTER = 0xA3
SENSORS_TYPE_REGISTER = 0xA4
NAME_REGISTER = 0xA5

# Function to get a register value as a string
def get_string_register(bus, address, register, length):
    write = i2c_msg.write(address, [register])
    read = i2c_msg.read(address, length)
    bus.i2c_rdwr(write, read)
    bytes_data = list(read)
    response_text = "".join(chr(byte) for byte in bytes_data)
    return response_text

# Function to get a register value as an integer
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
    
    counter = 1

    data_array = []

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
            version_hash = get_int_register(bus, i, VERSION_HASH_REGISTER, 32)
            # Display only the first 8 hexadecimal characters of the hash
            version_hash_short = hex(version_hash)[2:10]
            group = get_int_register(bus, i, GROUP_REGISTER, 1)
            sensors_type = get_string_register(bus, i, SENSORS_TYPE_REGISTER, 32)
            name = get_string_register(bus, i, NAME_REGISTER, 32)

            data_array.append([str(counter) + ".", hex(id), hex(i), "0x" + version_hash_short, str(group), sensors_type, name])
            
            counter += 1

    # Header of the table
    array_header = ("#", "UUID", "I2C", "Firmware", "Group", "Type", "Name")

    # Remove \x00 from data_array
    data_array = [[element.replace('\x00', '') for element in line] for line in data_array]

    # Find the maximum size of each column, including the length of the column title
    column_max_size = [max(len(str(element)) for element in column + (array_header[i],)) for i, column in enumerate(zip(*data_array))]

    # Add two spaces between each column
    column_max_size = [element + 2 for element in column_max_size]

    # Separator line
    separator_line = "-" * (sum(column_max_size) + len(column_max_size) - 1)

    if len(data_array) < 1:
        print("No i2c devices compatible with the ecosystem detected")
        return

    print(separator_line)

    # Header of the table
    for i, header in enumerate(array_header):
        print(f"{header:<{column_max_size[i]}}", end=" ")
    print()

    print(separator_line)

    # Print the data
    for line in data_array:
        for i, element in enumerate(line):
            print(f"{element:<{column_max_size[i]}}", end=" ")
        print()


    
if __name__ == '__main__':
    detect()