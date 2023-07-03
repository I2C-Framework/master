from smbus2 import SMBus, i2c_msg
import os
import math
import time
import sys

slave_address = 0x13
FIRMWARE_REGISTER = 0x10
FIRMWARE_PATH = "./store-data_alone.bin"

# Get slave address as application argument
slave_address = 0x00
if(len(sys.argv) != 2):
    print("Error: slave address not provided")
    sys.exit()
else:
    slave_address = int(sys.argv[1], 16)

with SMBus(1) as bus:
    
    file_size = os.path.getsize(FIRMWARE_PATH)
    
    # open firmware file
    firmware = open(FIRMWARE_PATH, "rb")
    
    firmware_content = bytearray(firmware.read())
    #print("Firmware content: " + str(list(firmware_content)))
    
    if(len(firmware_content) != file_size):
        print("Error: file size does not match")
           
    msg = i2c_msg.write(slave_address, [FIRMWARE_REGISTER])
    bus.i2c_rdwr(msg)
    time.sleep(1)

    # Send file as part of 2048 byte chunks
    for i in range(0, file_size, 2048):
        chunk = []
        if(i + 2048 > file_size):
            chunk = firmware_content[i:]
        else:
            chunk = firmware_content[i:i+2048]
        # Print chunck number
        print("Chunk number: " + str(i//2048+1) + " of " + str(math.ceil(file_size/2048)))
        # Message format: [register, block number, number of blocks in file, data]
        msg = i2c_msg.write(slave_address, [i//2048+1, math.ceil(file_size/2048)] + list(chunk))
        bus.i2c_rdwr(msg)
        # Wait for 10ms
        time.sleep(0.01)