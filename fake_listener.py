import serial
import time
import re
from typing import Generator
from classes import *
import sqlalchemy as sql
import getpass


username = getpass.getuser()
password = getpass.getpass("Database password: ")
engine = sql.create_engine(
    f"postgresql+psycopg2://{username}:{password}@localhost/heating"
)

COLUMN_NAMES = "(timecode,\
ground_floor_requesting, ground_floor_heating, ground_floor_time_heating, ground_floor_delay,\
bathroom_requesting, bathroom_heating, bathroom_time_heating, bathroom_delay,\
blue_room_requesting, blue_room_heating, blue_room_time_heating, blue_room_delay,\
j_bedroom_requesting, j_bedroom_heating, j_bedroom_time_heating, j_bedroom_delay,\
km_bedroom_requesting, km_bedroom_heating, km_bedroom_time_heating, km_bedroom_delay,\
top_floor_requesting, top_floor_heating, top_floor_time_heating, top_floor_delay)"
INSERT_VALUE_STRING = "(:timecode,\
:ground_floor_requesting, :ground_floor_heating, :ground_floor_time_heating, :ground_floor_delay,\
:bathroom_requesting, :bathroom_heating, :bathroom_time_heating, :bathroom_delay,\
:blue_room_requesting, :blue_room_heating, :blue_room_time_heating, :blue_room_delay,\
:j_bedroom_requesting, :j_bedroom_heating, :j_bedroom_time_heating, :j_bedroom_delay,\
:km_bedroom_requesting, :km_bedroom_heating, :km_bedroom_time_heating, :km_bedroom_delay,\
:top_floor_requesting, :top_floor_heating, :top_floor_time_heating, :top_floor_delay)"


class FakeArduino:
    """
    Class to mimick the output of the Arduino.

    >>> 'We have Arduino at home.'
    >>> The Arduino at home:
    """

    def __init__(self) -> None:
        self.gen = self.faker()

    def faker(self) -> Generator:
        while True:
            with open("fake_serial.txt", "rb") as file:
                lines = file.readlines()
                for line in lines:
                    time.sleep(0.01)
                    if line == b"\r\n":
                        time.sleep(0.18)
                    yield line

    def readline(self) -> bytes:
        return self.gen.__next__()


heating_zone: list[HeatingZone] = []
heating_zone.append(HeatingZone("Ground floor", 3))
heating_zone.append(HeatingZone("Bathroom", 2))
heating_zone.append(HeatingZone("Blue room", 1))
heating_zone.append(HeatingZone("J bedroom", 1))
heating_zone.append(HeatingZone("KM bedroom", 1))
heating_zone.append(HeatingZone("Top floor", 1))
full_cycle = False

arduino = FakeArduino()
while True:
    read_data = arduino.readline()

    if not read_data == b'':
        print(read_data)
    if len(read_data) < 8:
        # ignored lines
        continue
    elif read_data[0:3] == b"[Th":
        # requesting info
        split_per_thermostat = read_data.split(b":")
        for zone, status in zip(heating_zone, split_per_thermostat[1:7]):
            zone.requesting = True if status[0:1] == b"1" else False
        # full_cycle enshures a full cycle has been read when writing to db
        full_cycle = True
    # one char slices are required for these checks 
    elif read_data[2:3] == b"]":
        # heating info (6 lines)
        zone_nr: int = int(read_data[1:2])
        # find second number in line
        # borrowed from Vincent Savard https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
        numbers = re.findall(rb"\d+", read_data[3:])
        heating_zone[zone_nr].time_heating = int(numbers[0])
        heating_zone[zone_nr].delay = int(numbers[1])
        # determine if room is heated (this contains a bug: can't detect room is heated
        # when it switches from requested heating to delayed heating for a second)
        if (
            heating_zone[zone_nr].time_heating == 0
            and heating_zone[zone_nr].delay == 600
        ):
            heating_zone[zone_nr].heating = False
        else:
            heating_zone[zone_nr].heating = True

    # write to db
    if read_data[0:3] == b"[5]" and full_cycle:
        timecode = round(time.time() * 10)
        dbdict: dict[str, bool | int] = {"timecode": timecode}
        for zone in heating_zone:
            dbdict.update(zone.database_dict())

        with engine.begin() as db:
            command = sql.text(
                f"INSERT INTO direct_history {COLUMN_NAMES} VALUES {INSERT_VALUE_STRING}"
            )
            db.execute(command, dbdict)
