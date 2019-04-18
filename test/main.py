import pycom
import socket
from network import LoRa
import time
import machine
import bme280_float
import CCS811
from imu import MPU6050

try:
    lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.setblocking(False)
    print ("lora on")
except:
    print ("lora off")

try:
    uart_com = machine.UART(1, pins=("P3", "P4"), baudrate=9600)
    print ("uart communication init complete\n")
except:
    print("uart raised an exception\n")

try:
    i2c = machine.I2C(0, I2C.MASTER, baudrate=100000)
    print ("i2c init complete\n")
except:
    print ("i2c raised an exception\n")

try:
    adc = ADC.('P22')

    print ("analog communication init complete\n")

except:
    print ("couldn't establish analog communication\n")

try:
    bme = bme280_float.BME280(i2c=i2c, address=0x77)
    print ("bme280 - temperature/pressure/humidity sensor ON\n")
except:
    print ("bme280 - temperature/pressure/humidity sensor OFF\n")

try:
    imu = MPU6050(i2c)
    print ("mpu6050 - accelerometer/gyroscope ON\n")
except:
    print ("mpu6050 - accelerometer/gyroscope OFF\n")

try:
    ccs = CCS811.CCS811(i2c=i2c, addr=91)
    print ("ccs811 - environmental sensor ON\n")
except:
    print ("ccs811 - environmental sensor OFF\n")

try:
    gasSensor = adc.channel(pin='P16')
    print ("mics5524 - gas sensor ON\n")
except:
    print ("mics5524 - gas sensor OFF\n")

try:
    while True:
        if ccs.data_ready():
            values = bme.read_compensated_data(result = None)
            s.send('eCO2: %d ppm, TVOC: %d ppb, temp: %.2f c, pres: %.2f pa, hum: %.2f, accelX: %.2f, accelY: %.2f , accelZ: %.2f ;' % (ccs.eCO2, ccs.tVOC, values[0], values[1]/256, values[2], imu.accel.x, imu.accel.y, imu.accel.z))
        else
            print ("could not gather sensor data")
        if uart_com.any():
            gps_location = uart_com.readline()
            print(gps_location)
        else
            print ("could not gather gps data")
        time.sleep(5)
except:
    print ("nothing worked")
