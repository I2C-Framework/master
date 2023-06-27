from smbus2 import SMBus, i2c_msg
import os
import math
import time

SLAVE_ADDRESS = 0x42
FIRMWARE_REGISTER = 0x10
FIRMWARE_PATH = "./store-data.bin"

with SMBus(1) as bus:
    
    file_size = os.path.getsize(FIRMWARE_PATH)
    
    # open firmware file
    firmware = open(FIRMWARE_PATH, "rb")
    
    firmware_content = bytearray(firmware.read())
    #print("Firmware content: " + str(list(firmware_content)))
    
    if(len(firmware_content) != file_size):
        print("Error: file size does not match")
           

    # Send file as part of 1024 byte chunks
    for i in range(0, file_size, 1024):
        chunk = []
        if(i + 1024 > file_size):
            chunk = firmware_content[i:]
        else:
            chunk = firmware_content[i:i+1024]
        # Print chunck number
        print("Chunk number: " + str(i//1024+1) + " of " + str(math.ceil(file_size/1024)))
        # Message format: [register, block number, number of blocks in file, data]
        msg = i2c_msg.write(SLAVE_ADDRESS, [FIRMWARE_REGISTER, i//1024+1, math.ceil(file_size/1024)] + list(chunk))
        bus.i2c_rdwr(msg)
        # Wait for 100ms
        time.sleep(0.01)