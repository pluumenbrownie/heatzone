import serial
import time
import re
from typing import Generator


def faker() -> Generator:
    while True:
        time.sleep(1)
        with open("fake_serial.txt", "rb") as file:
            lines = file.readlines()
            for line in lines:
                time.sleep(0.01)
                yield line


class HeatingZone:
    def __init__(self, name: str, priority: int) -> None:
        self.name: str = name
        self.priority: int = priority
        self.requesting: bool = False
        self.heating: bool = False
        self.time_heating: int = 0
        self.delay: int = 600

    def __str__(self) -> str:
        if self.heating:
            if self.requesting:
                return f"{self.name:>12s} || {'    R' if self.requesting else 'Not r'}equesting | Heating on | On for {self.time_heating:>3d} s"
            else:
                return f"{self.name:>12s} || {'    R' if self.requesting else 'Not r'}equesting | Heating on | On for {self.time_heating:>3d} s | Delay left: {self.delay} s"
        else:
            return f"{self.name:>12s} || {'    R' if self.requesting else 'Not r'}equesting | Heating off"
    
    def __repr__(self) -> str:
        return f"{self.name}"


heating_zone: list[HeatingZone] = []
heating_zone.append(HeatingZone("Ground floor", 3))
heating_zone.append(HeatingZone("Bathroom", 2))
heating_zone.append(HeatingZone("Bedroom 1", 1))
heating_zone.append(HeatingZone("Bedroom 2", 1))
heating_zone.append(HeatingZone("Bedroom 3", 1))
heating_zone.append(HeatingZone("Top floor", 1))

# # with faker() as arduino:
# while True:
#     read_data = arduino.readline()
for read_data in faker():
    if read_data:
        print(read_data)

    if len(read_data) < 8:
        continue
    elif read_data[0:3] == b"[Th":
        split_per_thermostat = read_data.split(b":")
        for zone, status in zip(heating_zone, split_per_thermostat[1:7]):
            zone.requesting = True if status[0:1] == b"1" else False
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
