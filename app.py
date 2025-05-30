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
    return render_template("login.html")

@app.route("/create_apt", methods=["GET"])
def render_form():
    return render_template("create.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")
@app.route("/view", methods=["GET"])
def view():
    return render_template('view.html', user_data=get_user_info('all'), appts=get_appts()[2:])

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
    pwd_row = stmt.fetchone()
    pwd_hash = pwd_row["password"]

    if not pwd_hash:
        flash("User does not exist")
        return redirect(url_for('login'))
    else:
        pwd = request.form.get("lpwd")
        if check_password_hash(pwd_hash ,pwd):
            session['user_data'] = get_user_info(email)
            return render_template("view.html", user_data=get_user_info('all'), appts=get_appts()[2:])
        else:
            flash("Your username or password in incorrect!")
            return redirect(url_for('login'))

@app.route("/add_appt", methods=["POST"])
def add_appt():
    db = get_db()
    user = session["user_data"]
    print(user)
    date = request.form.get("date")
    time = request.form.get("time")
    query = db.execute("SELECT date, start_time from appointments WHERE user_id = ? AND start_time = ? AND date = ?", [user, time, date])
    datum = query.fetchall()
    if datum:
        flash("You already have an appointment scheduled for this time")
        return redirect(url_for('render_form'))
    else:
        db.execute("INSERT into appointments (user_id, date, start_time) VALUES (?, ?, ?)", [user, date, time])
        db.commit()
        flash("Appointment Confirmed")
        return render_template('view.html', user_data=get_user_info('all'), appts=get_appts()[2:])


@app.route("/delete", methods=["POST"])
def delete():
    pass

@app.route("/confirm_edit", methods=["POST"])
def confirm_edit():
    db = get_db()
    check = session['check']
    appt = request.form.get("appt")
    print(f"Received appt: {appt}")
    confirm = request.form.get("confirm")
    print(confirm)

    if check == "1" and confirm == "yes":
        db.execute("DELETE FROM appointments WHERE id = ?", (appt,))
        db.commit()
        flash("Changes confirmed!")
        return redirect(url_for('view'))
    elif check == "0" and confirm == "yes":
        date = request.form.get("date")
        time = request.form.get("time")
        db.execute("UPDATE appointments SET date = ?, start_time = ? WHERE id = ?", (date, time ,appt))
        db.commit()
        flash("Changes confirmed!")
        return redirect(url_for('view'))
    else:
        flash("Changes aborted!")
        return redirect(url_for('view'))

@app.route("/edit_data", methods=["POST"])
def edit_data():
    oldTime = request.form.get("oldTime")
    oldDate = request.form.get("oldDate")

    new_time = request.form.get("time")
    new_date = request.form.get("date")
    appt_id = request.form.get("appt")

    return render_template("confirm.html", newTime=new_time, newDate=new_date, id=appt_id, oldTime=oldTime, oldDate=oldDate)



@app.route("/edit", methods=["POST"])
def edit():
    db = get_db()
    check = request.form.get("check")
    session['check'] = check
    appt = request.form.get("appt_num")

    if check == "1":
        query = db.execute("SELECT id, date, start_time FROM appointments WHERE id = ?", (appt,))
        query = query.fetchone()
        return render_template("confirm.html", appt_datum = query, check=check)
    else:
        data = sel_appts(appt)
        return render_template("edit.html", appt_data=data)








def get_user_info(uname):
    db = get_db()
    if uname.lower() == 'all':
        query = db.execute("SELECT DISTINCT * FROM users")
        udata = query.fetchall()
        return udata
    else:
        query = db.execute("SELECT * FROM users WHERE email = ?", [uname])
        udata = query.fetchone()
        try:
            return udata[0]

        except IndexError:
           print(1)
           return "No data Found"


def get_appts():
    db = get_db()
    query = db.execute("SELECT DISTINCT appointments.id, first_name, last_name, date, start_time, end_time FROM appointments JOIN users ON users.id = appointments.user_id")
    adata = query.fetchall()
    try:
        return adata

    except IndexError:
        return "No data Found"

def sel_appts(appt):
    db = get_db()
    query= db.execute("SELECT * FROM appointments WHERE appointments.id = ?", (appt))
    adata = query.fetchone()
    return adata

def check_deadline():
    pass

def to_UTC():
    pass











