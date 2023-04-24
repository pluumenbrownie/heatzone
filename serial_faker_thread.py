import serial
import time
import re
from typing import Generator
from classes import *


def faker() -> Generator:
    while True:
        time.sleep(1)
        with open("fake_serial.txt", "rb") as file:
            lines = file.readlines()
            for line in lines:
                time.sleep(0.01)
                yield line


def get_serial_data() -> list[HeatingZone]: # type: ignore
    """
    Returns list of `HeatZones` with fake data from `fake_serial.txt`
    """
    heating_zone: list[HeatingZone] = []
    heating_zone.append(HeatingZone("Ground floor", 3))
    heating_zone.append(HeatingZone("Bathroom", 2))
    heating_zone.append(HeatingZone("Bedroom 1", 1))
    heating_zone.append(HeatingZone("Bedroom 2", 1))
    heating_zone.append(HeatingZone("Bedroom 3", 1))
    heating_zone.append(HeatingZone("Top floor", 1))

    full_cycle = False
    for read_data in faker():

        if len(read_data) < 8:
            continue
        elif read_data[0:3] == b"[Th":
            split_per_thermostat = read_data.split(b":")
            for zone, status in zip(heating_zone, split_per_thermostat[1:7]):
                zone.requesting = True if status[0:1] == b"1" else False
            full_cycle = True
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
        if read_data[0:3] == b"[5]" and full_cycle:
            return heating_zone


if __name__ == '__main__':
    get_serial_data()
