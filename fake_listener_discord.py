# Discord integration largely from 
# https://github.com/Rapptz/discord.py/blob/master/examples/background_task.py
from discord.ext import tasks
import discord

import serial
import re
from typing import Generator
from classes import *
import sqlalchemy as sql
import getpass
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from asyncio import sleep
from time import time, localtime, struct_time, asctime
import time as tm


USERNAME = getpass.getuser()
PASSWORD = getpass.getpass("Database password: ")
DISCORD_KEY = getpass.getpass("Discord API key: ")

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
                    tm.sleep(0.01)
                    if line == b"\r\n":
                        tm.sleep(0.18)
                    yield line

    def readline(self) -> bytes:
        return self.gen.__next__()


class MyClient(discord.Client):
    async def setup_hook(self) -> None:
        """
        Runs on startup.
        """
        # start the task to run in the background
        self.engine = create_engine(
            f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@localhost/heating"
        )
        self.latest_error: tuple[OperationalError, struct_time] | None = None

        # user ids of admins can be put in the database
        with self.engine.begin() as db:
            command = sql.text(f"SELECT * FROM discord_admins")
            results = db.execute(command).all()
        self.admins = [entry[0] for entry in results]

    async def on_ready(self) -> None:
        """
        Also runs on startup, but later.
        """
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        self.run_listener.start()
        await self.send_to_admins("Bot is on")
    
    def update_error(self, error: OperationalError):
        """
        Set the `self.latest_error` property to a new error and time. 
        """
        self.latest_error = (error, localtime())

    async def send_to_admins(self, message):
        """
        Sends a message to the users associated with the ids in the
        `discord_admins` database table.
        """
        for user_id in self.admins:
            # from https://stackoverflow.com/questions/70781117/how-do-you-send-a-private-message-on-ready-aka-on-a-client-event-discord-py
            user = await client.fetch_user(user_id)
            await user.send(message)
    
    async def listener_failed(self) -> None:
        """
        Send a message to the admins and set the presence to Do Not Disturb.
        """
        await self.send_to_admins("Listener fallback failed.")
        await client.change_presence(status=discord.Status.do_not_disturb)

    @tasks.loop(count=1, reconnect=True)
    async def run_listener(self) -> None:
        """
        The listener, rewritten to use async.
        """
        await client.change_presence(status=discord.Status.online)

        heating_zone: list[HeatingZone] = []
        heating_zone.append(HeatingZone("Ground floor", 3))
        heating_zone.append(HeatingZone("Bathroom", 2))
        heating_zone.append(HeatingZone("Blue room", 1))
        heating_zone.append(HeatingZone("J bedroom", 1))
        heating_zone.append(HeatingZone("KM bedroom", 1))
        heating_zone.append(HeatingZone("Top floor", 1))
        full_cycle = False

        arduino = FakeArduino()
        # async: loop stops when disconnected.
        while not client.is_closed():
            # async: i hope this readline won't block to much
            read_data = arduino.readline()

            if not read_data == b'':
                print(read_data)
            
            if len(read_data) < 3:
                await sleep(0.05)
                continue
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
                timecode = round(time() * 10)
                dbdict: dict[str, bool | int] = {"timecode": timecode}
                for zone in heating_zone:
                    dbdict.update(zone.database_dict())

                try:
                    # async: maybe change to https://docs.sqlalchemy.org/en/20/_modules/examples/asyncio/basic.html
                    with self.engine.begin() as db:
                        command = sql.text(
                            f"INSERT INTO direct_history {COLUMN_NAMES} VALUES {INSERT_VALUE_STRING}"
                        )
                        db.execute(command, dbdict)
                except OperationalError as error:
                    # retry when writing to db fails
                    await self.send_to_admins("Database error detected, trying fallback.")
                    self.update_error(error)
                    await sleep(0.1)
                    try:
                        with self.engine.begin() as db:
                            command = sql.text(
                                f"INSERT INTO direct_history {COLUMN_NAMES} VALUES {INSERT_VALUE_STRING}"
                            )
                            db.execute(command, dbdict)
                    except OperationalError as error:
                        print(error)
                        self.update_error(error)
                        break
        await self.listener_failed()

    @run_listener.before_loop
    async def before_my_task(self):
        """
        Only start the listener when connected to Discord.
        """
        await self.wait_until_ready()  # wait until the bot logs in

    async def on_message(self, message: discord.Message):
        """
        Parses commands.
        """
        # only admins should be able to message the bot
        if message.author.id not in self.admins:
            return
        
        if message.content.startswith("weup"):
            if self.run_listener.is_running():
                await message.reply("We're still running!")
            else:
                await message.reply("We're down :(")

        elif message.content.startswith("restart"):
            if not self.run_listener.is_running():
                await message.reply("Restarting...")
                self.run_listener.start()
            else:
                await message.reply("Listener is already running.")
        
        elif message.content.startswith("error"):
            if self.latest_error:
                await message.reply(f"This was the latest error:\n{self.latest_error[0]}\n@ {asctime(self.latest_error[1])}")
            else:
                await message.reply("No errors to show yet.")
        
        elif message.content.startswith("help"):
            await message.reply("Possible commands:\n\t- weup --- See if the listener is still running\n\t- restart --- Restart the listener if it has crashed\n\t- error --- Print the latest error message")



client = MyClient(intents=discord.Intents.default())
client.run(DISCORD_KEY)