from smbus2 import SMBus, i2c_msg
import time

ID_REGISTER = 0x1
MAJOR_VERSION_REGISTER = 0x2
MINOR_VERSION_REGISTER = 0x3
FIX_VERSION_REGISTER = 0x4



# Function to send message vy i2c
def send_message(bus, address, register, length):
    # Write ID register
    msg = i2c_msg.write(address, [register])
    # Send message
    bus.i2c_rdwr(msg)
    # Read ID register
    msg = i2c_msg.read(address, length)
    # Send message
    bus.i2c_rdwr(msg)
    data = 0
    for i in range(0, length):
        data += int.from_bytes(msg.buf[i], byteorder='big') << (8*i)
    return data

    
bus = SMBus(1)    

print("#  uuid        i2c      firmware")
print("--------------------------------")
counter = 0

# Detect all devices
for i in range(0x10, 0x78):
    # Write ID register
    msg = i2c_msg.read(i, 1)
    # Send message
    try:
        bus.i2c_rdwr(msg)
    except:
        pass
    # Check if response is 0x97
    if(int.from_bytes(msg.buf[0], byteorder='big') == 0x97):
        id = send_message(bus, i, ID_REGISTER, 4)
        major_version = send_message(bus, i, MAJOR_VERSION_REGISTER, 2)
        minor_version = send_message(bus, i, MINOR_VERSION_REGISTER, 2)
        fix_version = send_message(bus, i, FIX_VERSION_REGISTER, 2)
        
        counter += 1
        
        print(str(counter) + ". " + hex(id) + "    " + hex(i) + "     " + str(major_version) + "." + str(minor_version) + "." + str(fix_version))
