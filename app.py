import json
import time
import getpass

import sqlalchemy as sql
from flask import Flask, render_template, request
from flask_session import Session

from classes import *
import graphs


COLUMN_NAMES = (
    "timecode",
    "ground_floor_requesting",
    "ground_floor_heating",
    "ground_floor_time_heating",
    "ground_floor_delay",
    "bathroom_requesting",
    "bathroom_heating",
    "bathroom_time_heating",
    "bathroom_delay",
    "blue_room_requesting",
    "blue_room_heating",
    "blue_room_time_heating",
    "blue_room_delay",
    "j_bedroom_requesting",
    "j_bedroom_heating",
    "j_bedroom_time_heating",
    "j_bedroom_delay",
    "km_bedroom_requesting",
    "km_bedroom_heating",
    "km_bedroom_time_heating",
    "km_bedroom_delay",
    "top_floor_requesting",
    "top_floor_heating",
    "top_floor_time_heating",
    "top_floor_delay",
)
ROOM_NAMES = (
    "ground_floor",
    "bathroom",
    "blue_room",
    "j_bedroom",
    "km_bedroom",
    "top_floor",
)


app = Flask(__name__, static_url_path="/static")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
# i find this an easier way to hande passwords, though you do need to
# reenter it every time the code is restarted
username = getpass.getuser()
password = getpass.getpass("Database password: ")
engine = sql.create_engine(
    f"postgresql+psycopg2://{username}:{password}@localhost/heating"
)


def determine_color(heating_zone: HeatingZone) -> str | None:
    if heating_zone.heating:
        return "svg_orange"
    elif heating_zone.requesting:
        return "svg_purple"


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/canvas")
def canvas() -> str:
    return render_template("canvas.html")


@app.route("/history")
def history() -> str:
    return render_template("history.html")


@app.route("/_get_status")
def get_status() -> str:
    with engine.begin() as db:
        output = db.execute(
            sql.text("SELECT * FROM direct_history ORDER BY timecode DESC LIMIT 1")
        ).first()
    dictionary: dict[str, str | int | bool] = {}

    if not output:
        return "error"

    for name, value in zip(COLUMN_NAMES, output):
        dictionary[name] = value

    add_colors_to_dict(dictionary)
    dictionary.update(
        {
            "ground_floor_name": "Ground floor",
            "bathroom_name": "Bathroom",
            "blue_room_name": "Blue room",
            "j_bedroom_name": "J bedroom",
            "km_bedroom_name": "KM bedroom",
            "top_floor_name": "Top floor",
        }
    )
    dictionary["timecode"] = time.strftime(
        "%H:%M:%S %d-%m-%Y", time.localtime(float(dictionary["timecode"]) / 10)
    ).__str__()

    return json.dumps(dictionary)


@app.post("/_get_graph")
def get_graph() -> str:
    """
    Generates svg graphs with graphs.py and returnes them in json format.
    """
    json_request = request.json
    if not json_request:
        return ""

    if json_request["type"] == "one_hour":
        roomname = json_request["roomname"]
        if not roomname:
            return ""
        return graphs.one_hour_history(roomname, engine).replace(
            'width="360" height="20"',
            'width="100%" height="100%" preserveAspectRatio="none"',
        )

    elif json_request["type"] == "one_day":
        json_graphs = graphs.day_history(engine)
        for key in json_graphs.keys():
            json_graphs[key] = json_graphs[key].replace(
                'width="360" height="20"',
                'width="100%" height="100%" preserveAspectRatio="none"',
                1,
            )
        return json.dumps(json_graphs)

    return ""


def add_colors_to_dict(dictionary: dict[str, str | int | bool]) -> None:
    for room in ROOM_NAMES:
        if dictionary[f"{room}_heating"]:
            dictionary.update({f"{room}_class": "svg_orange"})
        elif dictionary[f"{room}_requesting"]:
            dictionary.update({f"{room}_class": "svg_purple"})
        else:
            dictionary.update({f"{room}_class": ""})
