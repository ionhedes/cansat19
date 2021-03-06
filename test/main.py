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
import machine
import math

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

if switch == True:
    print("\n----------------------------------\nEntering main loop...\n----------------------------------\n")
    pycom.heartbeat(True)
    last_acceleration = 0
    current_acceleration = 0
    last_time = 0
    current_time = 0
    last_speed = 0
    current_speed = 0
    packet_no = 0
    while True:
        current_time = time.time()
        gps_data_ready = False
        sensor_data_ready = False
        try:
            if uart_com.any():
                gps_location = uart_com.readline()
                nmea_parser.parse(gps_location)
                gps_data_ready = True
            else:
                print (" ! Could not gather GPS data")
            if ccs.data_ready():
                values = bme.read_compensated_data(result = None)
                sensor_data_ready = True
            else:
                print (" ! Could not gather sensor data\n")
        except:
            print (" ! Error, rebooting...\n")
            machine.reset()

        if gps_data_ready == True and sensor_data_ready == True:
            packet_no+=1;
            current_acceleration = math.sqrt(math.fabs((imu.accel.x*10) ** 2 + (imu.accel.y*10) ** 2 + (imu.accel.z*10) ** 2)) - 9.87
            current_speed = last_speed + (current_acceleration - last_acceleration)*(current_time - last_time)
            current_speed = math.fabs((current_speed - (current_speed - math.floor(current_speed)))/10)
            raw_data = '92,%d,%d,%s,%s,%s,%s,%d,%d,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f'% (current_time, packet_no, nmea_parser.date, nmea_parser.time, nmea_parser.latitude, nmea_parser.longitude, ccs.eCO2, ccs.tVOC, values[0], values[1]/100, values[2], bme.altitude, imu.accel.x*10, imu.accel.y*10, imu.accel.z*10, current_speed)
            encoded_data = raw_data.encode('utf-8')
            s.send(encoded_data)
            print("Data sent..")

        last_time = current_time
        last_acceleration = current_acceleration
        last_speed = current_speed
        time.sleep(5)

if switch == False:
    print (" ! Error, rebooting...\n")
    machine.reset()
