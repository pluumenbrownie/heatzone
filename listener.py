import serial
import time
import re
from classes import *
import sqlalchemy as sql
import getpass


username = getpass.getuser()
password = getpass.getpass("Database password: ")
engine = sql.create_engine(f"postgresql+psycopg2://{username}:{password}@localhost/heating")

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


heating_zone: list[HeatingZone] = []
heating_zone.append(HeatingZone("Ground floor", 3))
heating_zone.append(HeatingZone("Bathroom", 2))
heating_zone.append(HeatingZone("Blue room", 1))
heating_zone.append(HeatingZone("J bedroom", 1))
heating_zone.append(HeatingZone("KM bedroom", 1))
heating_zone.append(HeatingZone("Top floor", 1))
full_cycle = False


with serial.Serial(port="/dev/ttyACM0", baudrate=9600, timeout=0.1) as arduino:
    while True:
        read_data = arduino.readline()

        print(read_data)
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
            timecode = round(time.time() * 10)
            dbdict: dict[str, bool|int] = {"timecode": timecode}
            for zone in heating_zone:
                dbdict.update(zone.database_dict())
            with engine.begin() as db:
                command = sql.text(
                    f"INSERT INTO direct_history {COLUMN_NAMES} VALUES {INSERT_VALUE_STRING}"
                    )
                db.execute(command, dbdict)
