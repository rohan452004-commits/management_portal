import os

import sqlite3


from flask import (

     Flask, render_template, request,

     redirect, url_for, flash, jsonify, g

)


app = Flask(__name__)


app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "mevi-workshop-development-key",
)


#Database configuration

os.makedirs(app.instance_path, exist_ok=True)


DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(app.instance_path, "management.db"),
)