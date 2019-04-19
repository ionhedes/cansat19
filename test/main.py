import pycom
import socket
from network import LoRa
import time
from machine import I2C
from machine import UART
import bme280_float
import CCS811
from imu import MPU6050
import os

'''print(os.uname())'''
switch = True;

try:
    print("\n----------------------------------\nStarting initialization process...\n----------------------------------\n")
    pycom.heartbeat(False)
    pycom.rgbled(0x7f7f00)
    try:
        lora = LoRa(mode=LoRa.LORA)
        s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        s.setblocking(False)
        print (" - LoRa on\n")
    except:
        print (" - LoRa off\n")

    try:
        uart_com = UART(1, pins=("P3", "P4"), baudrate=9600)
        print (" . UART communication init complete\n")
    except:
        print(" ! UART raised an exception\n")

    try:
        i2c = I2C(0, I2C.MASTER, baudrate=100000)
        print (" . I2C init complete\n")
    except:
        print (" ! I2C raised an exception\n")

    try:
        bme = bme280_float.BME280(i2c=i2c, address=0x77)
        print (" . BME280 - temperature/pressure/humidity sensor ON\n")
    except:
        print (" ! BME280 - temperature/pressure/humidity sensor OFF\n")

    try:
        imu = MPU6050(i2c)
        print (" . MPU6050 - accelerometer/gyroscope ON\n")
    except:
        print (" ! MPU6050 - accelerometer/gyroscope OFF\n")

    try:
        ccs = CCS811.CCS811(i2c=i2c, addr=91)
        print (" . CCS811 - environmental sensor ON\n")
    except:
        print (" ! ccs811 - environmental sensor OFF\n")

except:
        print("\n----------------------------------\nInitialization failed...\n----------------------------------\n")
        switch = False;
        pycom.heartbeat(False)
        pycom.rgbled(0x7f0000)

if switch:
    print("\n----------------------------------\nEntering main loop...\n----------------------------------\n")
    pycom.heartbeat(True)
    while True:
        if ccs.data_ready():
            values = bme.read_compensated_data(result = None)
            s.send('eCO2: %d ppm, TVOC: %d ppb, temp: %.2f c, pres: %.2f pa, hum: %.2f, accelX: %.2f, accelY: %.2f , accelZ: %.2f ;' % (ccs.eCO2, ccs.tVOC, values[0], values[1]/256, values[2], imu.accel.x, imu.accel.y, imu.accel.z))
            print('eCO2: %d ppm, TVOC: %d ppb, temp: %.2f c, pres: %.2f pa, hum: %.2f, accelX: %.2f, accelY: %.2f , accelZ: %.2f ;\n '% (ccs.eCO2, ccs.tVOC, values[0], values[1]/256, values[2], imu.accel.x, imu.accel.y, imu.accel.z))
        else:
            print (" ! Could not gather sensor data\n")
        if uart_com.any():
            gps_location = uart_com.readline()
            s.send(gps_location)
            print(gps_location + '\n')
        else:
            print (" ! Could not gather GPS data\n")
        time.sleep(5)
