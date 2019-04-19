import pycom
from network import LoRa
import socket
import time

switch = True

try:
    print("\n----------------------------------\nStarting initialization process...\n----------------------------------\n")
    pycom.heartbeat(False)
    pycom.rgbled(0x7f7f00)
    try:
        lora = LoRa(mode=LoRa.LORA, frequency=434900000)
        s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        s.setblocking(False)
        print (" . LoRa on\n")
    except:
        print (" ! LoRa off\n")

except:
    print("\n----------------------------------\nInitialization failed...\n----------------------------------\n")
    switch = False;
    pycom.heartbeat(False)
    pycom.rgbled(0x7f0000)

if switch:
    print("\n----------------------------------\nEntering main loop...\n----------------------------------\n")
    pycom.heartbeat(True)
    while True:
        data = s.recv(64)
        if data:
            print(data.decode('utf-8'))
        time.sleep(7)
