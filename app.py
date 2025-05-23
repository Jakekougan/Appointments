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
        sql_script = f.read()
        print(sql_script)
        db.cursor().executescript(sql_script)
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
    return render_template("login.html")

@app.route("/create_acc", methods=["GET"])
def create_account():
    return render_template("create_account.html")

@app.route("/add_user", methods=["POST"])
def add_user():
    db = get_db()

    fname = request.form.get("rfname")
    lname = request.form.get("rlname")
    email = request.form.get("remail")
    pnum = request.form.get("rpnum")
    pwd = request.form.get("rpwd")
    cpwd = request.form.get("rcpwd")

    if pwd != cpwd:
        flash("Passwords do not match!")
        return render_template("create_account.html", fname=fname, lname=lname, email=email, pnum=pnum)
    else:
        pwd = generate_password_hash(pwd, salt_length=11)
        db.execute("INSERT INTO users (first_name, last_name, email, phone_number, password) VALUES (?,?,?,?,?)",
                [fname, lname, email, pnum, pwd])
        db.commit()
        flash("Account created!")
        return render_template("login.html")

@app.route("/auth", methods=["POST"])
def user_auth():
    #Get data from login form
    db = get_db()
    email = request.form.get("lemail")
    stmt = db.execute("SELECT password FROM users WHERE email = ?", [email])
    pwd_hash = stmt.fetchone()
    print(pwd_hash)
    if not pwd_hash:
        flash("User does not exist")
        return redirect(url_for('login'))
    else:
        pwd = request.form.get("lpwd")
        if check_password_hash(pwd_hash[0],pwd):
            return render_template("index.html")
        else:
            flash("Your username or password in incorrect!")
            return redirect(url_for('login'))









