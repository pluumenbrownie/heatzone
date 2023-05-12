
import os
import json
import time
import getpass

import sqlalchemy as sql
from flask import Flask, flash, session, redirect, render_template, request
from flask_session import Session
from markupsafe import Markup

from classes import *


COLUMN_NAMES = ("timecode",
"ground_floor_requesting", "ground_floor_heating", "ground_floor_time_heating", "ground_floor_delay",
"bathroom_requesting", "bathroom_heating", "bathroom_time_heating", "bathroom_delay",
"blue_room_requesting", "blue_room_heating", "blue_room_time_heating", "blue_room_delay",
"j_bedroom_requesting", "j_bedroom_heating", "j_bedroom_time_heating", "j_bedroom_delay",
"km_bedroom_requesting", "km_bedroom_heating", "km_bedroom_time_heating", "km_bedroom_delay",
"top_floor_requesting", "top_floor_heating", "top_floor_time_heating", "top_floor_delay")
ROOM_NAMES = ("ground_floor", "bathroom", "blue_room", "j_bedroom", "km_bedroom", "top_floor")

app = Flask(__name__, static_url_path="/static")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
username = getpass.getuser()
password = getpass.getpass("Database password: ")
engine = sql.create_engine(f"postgresql+psycopg2://{username}:{password}@localhost/heating")


def determine_color(heating_zone: HeatingZone) -> str | None:
    if heating_zone.heating:
        return "svg_orange"
    elif heating_zone.requesting:
        return "svg_purple"
    

@app.route("/")
def index() -> str:
    return render_template("index.html", data_ip="http://192.168.1.135:5000/_get_status")
    

@app.route("/fake")
def fake_index() -> str:
    return render_template("index.html", data_ip="http://127.0.0.1:5000/_get_status")


@app.route("/_get_status")
def get_status() -> str:
    with engine.begin() as db:
        output = db.execute(sql.text("SELECT * FROM direct_history ORDER BY timecode DESC LIMIT 1")).first()
    dictionary: dict[str, str|int|bool] = {}
 
    if not output:
        return "error"
    
    for name, value in zip(COLUMN_NAMES, output):
        dictionary[name] = value

    add_colors_to_dict(dictionary)
    
    return json.dumps(dictionary)


def add_colors_to_dict(dictionary: dict[str, str|int|bool]) -> None:
    for room in ROOM_NAMES:
        if dictionary[f"{room}_heating"]:
            dictionary.update({f"{room}_class": "svg_orange"})
        elif dictionary[f"{room}_requesting"]:
            dictionary.update({f"{room}_class": "svg_purple"})
        else:
            dictionary.update({f"{room}_class": ""})

    