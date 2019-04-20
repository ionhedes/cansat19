import pycom
import socket
from network import LoRa
import time
from machine import I2C
from machine import UART
import bme280_float
import CCS811
from imu import MPU6050
import nmea
import os

'''print(os.uname())'''
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
        print (" ! CCS811 - environmental sensor OFF\n")

    try:
        nmea_parser = nmea.nmea(debug=1)
        print (" . NMEA parser ON\n")
    except:
        print (" ! NMEA parser OFF\n")

except:
        print("\n----------------------------------\nInitialization failed...\n----------------------------------\n")
        switch = False;
        pycom.heartbeat(False)
        pycom.rgbled(0x7f0000)

if switch:
    print("\n----------------------------------\nEntering main loop...\n----------------------------------\n")
    pycom.heartbeat(True)
    while True:
        if uart_com.any():
            gps_location = uart_com.readline()
            nmea_parser.parse(gps_location)
            if nmea_parser.date == '01/01/2000' or nmea_parser.time == '00:00:00' or nmea_parser.latitude == '0' or nmea_parser.longitude == '0':
                print(" * GPS signal not fixed yet")
            else:
                gps_location_raw = '%s,%s,%s,%s'% (nmea_parser.date, nmea_parser.time, nmea_parser.latitude, nmea_parser.longitude)
                gps_location_encoded = gps_location_raw.encode('utf-8')
                s.send(gps_location_encoded)
                print('date: %s, time %s, latitude %s, longitude %s;'% (nmea_parser.date, nmea_parser.time, nmea_parser.latitude, nmea_parser.longitude))
        else:
            print (" ! Could not gather GPS data")

        if ccs.data_ready():
            values = bme.read_compensated_data(result = None)
            raw_data = '%d,%d,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f;'% (ccs.eCO2, ccs.tVOC, values[0], values[1]/256, values[2], imu.accel.x, imu.accel.y, imu.accel.z)
            encoded_data = raw_data.encode('utf-8')
            s.send(encoded_data)
            print('eCO2: %d ppm, TVOC: %d ppb, temp: %.2f c, pres: %.2f pa, hum: %.2f, accelX: %.2f, accelY: %.2f , accelZ: %.2f ;\n '% (ccs.eCO2, ccs.tVOC, values[0], values[1]/256, values[2], imu.accel.x*10, imu.accel.y*10, imu.accel.z*10))
        else:
            print (" ! Could not gather sensor data\n")

        time.sleep(5)
