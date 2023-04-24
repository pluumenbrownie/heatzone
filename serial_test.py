import serial
import time
import re
from classes import *


heating_zone: list[HeatingZone] = []
heating_zone.append(HeatingZone("Ground floor", 3))
heating_zone.append(HeatingZone("Bathroom", 2))
heating_zone.append(HeatingZone("Bedroom 1", 1))
heating_zone.append(HeatingZone("Bedroom 2", 1))
heating_zone.append(HeatingZone("Bedroom 3", 1))
heating_zone.append(HeatingZone("Top floor", 1))

with serial.Serial(port="/dev/ttyACM0", baudrate=9600, timeout=0.1) as arduino:
    while True:
        read_data = arduino.readline()

        if read_data:
            print(read_data)

        if len(read_data) < 8:
            continue
        elif read_data[0:3] == b"[Th":
            split_per_thermostat = read_data.split(b":")
            for zone, status in zip(heating_zone, split_per_thermostat[1:7]):
                zone.requesting = True if status[0] == b"1" else False
        elif read_data[2:3] == b"]":
            zone_nr: int = int(read_data[1:2])
            numbers = re.findall(br"\d+", read_data[3:])
            heating_zone[zone_nr].time_heating = int(numbers[0])
            heating_zone[zone_nr].delay = int(numbers[1])
            if (
                heating_zone[zone_nr].time_heating == 0
                and heating_zone[zone_nr].delay == 600
            ):
                heating_zone[zone_nr].heating = False
            else:
                heating_zone[zone_nr].heating = True
        if read_data[0:3] == b"[5]":
            for zone in heating_zone:
                print(zone)
            print(" ")
