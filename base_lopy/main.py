import pycom
from network import LoRa
import socket
import time
import machine

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

if switch == True:
    print("\n----------------------------------\nEntering main loop...\n----------------------------------\n")
    pycom.heartbeat(True)
    while True:
        try:
            data = s.recv(128)
            if data:
                data_decoded = data.decode('utf-8')
                decoded_data = data.decode('utf-8')
                if decoded_data[0] == '9' and decoded_data[1] == '2':
                    print(data_decoded)
                    with open("log.csv", "a+") as f:
                        f.write(data_decoded + '\n')
                else:
                    print("Foreign data, ignoring..")
            else:
                print("No data..\n")
        except:
            print (" ! Error, rebooting...\n")
            machine.reset()
        time.sleep(5)

if switch == False:
    print (" ! Rebooting...\n")
    machine.reset()
