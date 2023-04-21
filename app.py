
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


app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.route("/")
def index():
    return render_template("index.html")