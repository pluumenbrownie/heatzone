
import os
import json
import time

from flask import Flask, flash, session, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import scoped_session, sessionmaker, aliased
import requests
from markupsafe import Markup

from classes import *
from serial_thread import get_serial_data


app = Flask(__name__, static_url_path="/static")


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


def determine_color(heating_zone):
    if heating_zone.heating:
        return "svg_orange"
    elif heating_zone.requesting:
        return "svg_purple"
    

@app.route("/")
def index() -> str:
    data = get_serial_data()
    data = [zone.__str__() for zone in data]
    return render_template("index.html", heatzonestrings=data, zone_data=data, determine_color=determine_color)
