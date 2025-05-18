import datetime
from flask import Flask, request, g, redirect, url_for, render_template, flash, session
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'userinfo.db'),
                       SECRET_KEY='development key'))

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_cmd():
    init_db()
    print("Initialized the database")

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/", methods=["GET"])
def main():
    return render_template("index.html")

@app.route("/create_apt", methods=["GET"])
def render_form():
    return render_template("create.html")

@app.route("/login", methods=["GET"])
def login():
    render_template("login.html")

@app.route("/create_acc", methods=["GET"])
def create_account():
    return render_template("create_account")