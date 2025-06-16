import datetime
from flask import Flask, request, g, redirect, url_for, render_template, flash, session
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

#load enviornment variables from .env file
load_dotenv()

app = Flask(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'userinfo.db'),
                       SECRET_KEY='development key'))

def connect_db():
    '''Establish connection to SQLite database

    Parameters:
        None

    Returns:
        SQLite connection object'''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    '''Creates a relational database based on the SQL statements in schema.sql file
    If there is data that already exists in the database it will be cleared

    Parameters:
        None

    Returns:
        None'''

    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        sql_script = f.read()
        db.cursor().executescript(sql_script)
    db.commit()

@app.cli.command('initdb')
def initdb_cmd():
    '''Allows the database to created or cleared from the command line
    Enter python -m flask initdb

    Parameters:
        None

    Returns:
        None
        '''
    init_db()
    print("Initialized the database")

def get_db():
    '''Checks if a connection object exists if not it will create one and then return it
    If an object exists it will return it

    Parameter:
        None

    Returns:
        SQLite database connection object'''

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    '''Closes the SQLite connection object in the event of an application or
    when the app is closed

    Parameters:
        error (Exception): an error that causes the application to crash

    Returns:
        None'''

    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route("/", methods=["GET"])
def main():
    '''Renders the login.html template when the web application is open'''

    return render_template("login.html")

@app.route("/create_apt", methods=["GET"])
def render_form():
    '''renders the create appointment form'''
    return render_template("create.html")

@app.route("/login", methods=["GET"])
def login():
    '''When clicking the logout button from the navbar, this route is called and sends user back to login page'''
    return render_template("login.html")

@app.route("/view", methods=["GET"])
def view():
    '''Sends user to the homepage and retrieves all the appointment data'''
    return render_template('view.html', user_data=get_user_info('all'), appts=get_appts(), ids=get_appt_ids())

@app.route("/create_acc", methods=["GET"])
def create_account():
    '''Renders the create account form'''
    return render_template("create_account.html")

@app.route("/add_user", methods=["POST"])
def add_user():
    '''Handles the logic of adding a new user to the database when a user submits the create account ford'''
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
        db.execute("INSERT INTO users (first_name, last_name, email, phone_number, password, type) VALUES (?,?,?,?,?,?)",
                [fname, lname, email, pnum, pwd, 0])
        db.commit()
        flash("Account created!")
        return render_template("login.html")

@app.route("/auth", methods=["POST"])
def user_auth():
    '''Handles the logic of ensuring the data entered in the login form matches a user in the database'''
    #Get data from login form
    email = request.form.get("lemail")
    pwd_row = get_user_info(email)

    if not pwd_row:
        flash("Your username or password is incorrect!")
        return redirect(url_for('login'))

    else:

        pwd_hash = pwd_row["password"]
        utype = pwd_row["type"]

        session["utype"] = utype
        session['user_data'] = get_user_info(email)


        pwd = request.form.get("lpwd")
        if check_password_hash(pwd_hash ,pwd):
            session['user_data'] = get_user_info(email)
            flash(f"Login Successful! Welcome {session['user_data'][1]} {session['user_data'][2]}")
            return redirect(url_for('view'))
        else:
            flash("Your username or password is incorrect!")
            return redirect(url_for('login'))


@app.route("/add_appt", methods=["POST"])
def add_appt():
    '''Handles logic for creating a new appointment '''
    db = get_db()
    user = session["user_data"]
    date = request.form.get("date")
    time = to12hr(request.form.get("time"))
    query = db.execute("SELECT date, start_time from appointments WHERE user_id = ? AND start_time = ? AND date = ?", [user, time, date])
    datum = query.fetchall()
    if datum:
        flash("You already have an appointment scheduled for this time")
        return redirect(url_for('render_form'))
    else:
        db.execute("INSERT into appointments (user_id, date, start_time) VALUES (?, ?, ?)", [user, date, time])
        db.commit()
        flash("Appointment Confirmed")
        return redirect(url_for('view'))

@app.route("/confirm_edit", methods=["POST"])
def confirm_edit():
    '''When trying to edit or delete an appointment user is prompted,
    asking for confirmation if they want to make the changes.
    Upon clicking yes this handler will handle the logic of deleting or
    editing the appointment.'''

    db = get_db()
    check = session['check']
    appt = request.form.get("appt")
    confirm = request.form.get("confirm")

    if check == "1" and confirm == "yes":
        db.execute("DELETE FROM appointments WHERE id = ?", (appt,))
        db.commit()
        flash("Changes confirmed!")
        return redirect(url_for('view'))
    elif check == "0" and confirm == "yes":
        print("no")
        date = request.form.get("date")
        time = to12hr(request.form.get("time"))
        db.execute("UPDATE appointments SET date = ?, start_time = ? WHERE id = ?", (date, time ,appt))
        db.commit()
        flash("Changes confirmed!")
        return redirect(url_for('view'))
    else:
        flash("Changes aborted!")
        return redirect(url_for('view'))

@app.route("/edit_data", methods=["POST"])
def edit_data():
    '''When editing an appointment this hanlder grabs the old and new data to be displayed
    when the user is prompted asking if they want to confirm the changes'''

    oldTime = request.form.get("oldTime")
    oldDate = request.form.get("oldDate")

    new_time = request.form.get("time")
    new_date = request.form.get("date")
    appt_id = request.form.get("appt")

    return render_template("confirm.html", newTime=new_time, newDate=new_date, id=appt_id, oldTime=oldTime, oldDate=oldDate)



@app.route("/edit", methods=["POST"])
def edit():
    '''Retireves the appointment from the database and its corresponding data to be
    prepopulated in the edit form'''

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
        time = to24hr(data[3])
        return render_template("edit.html", appt_data=data, time=time)


#Helper Functions

def get_user_info(uname):
    '''Get all the info stored in the database tied to a certain user

    Parameter:
        uname (str): the email address of a user entered as a string

    Returns:
        An SQL row object containing the data tied to that user'''

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
    '''Retrieves all the appointments stored in the database

    Parameters:
        None

    Returns:
        SQL row object containing data from every row in the appointments table'''

    db = get_db()
    query = db.execute("SELECT DISTINCT appointments.id, first_name, last_name, date, start_time, end_time FROM appointments JOIN users ON users.id = appointments.user_id")
    adata = query.fetchall()
    try:
        return adata

    except IndexError:
        return "No data Found"

def sel_appts(appt):
    '''Gets all the data for a certian appointment based on its primary key

    Parameter:
        appt (int): the primary key for an appointment's row in the table

    Returns:
        the data tied to a certain appointment'''

    db = get_db()
    query= db.execute("SELECT * FROM appointments WHERE appointments.id = ?", (appt,))
    adata = query.fetchone()
    return adata

def get_appt_ids():
    '''retrieves all for the primary keys from the appointments table

    Parameters:
        None

    Returns:
        a collection of appointment ids'''

    db = get_db()
    query = db.execute("SELECT id FROM appointments")
    ids = query.fetchall()
    return ids

def to12hr(time):
    '''HTML time inputs only take the data in 24 hour, this function converts it back into 12 hour time

    Parameters:
        time (str): the time in 24 hour time as a string

    Returns:
        The original inputted time in 12 hour format'''

    spring = time.split(':')
    hour = int(spring[0])
    min = spring[1]
    period = ""
    if hour > 12:
        hour -= 12
        period = "PM"

    elif hour == 12:
        period = "PM"

    elif hour == 0:
        hour = 12
        period = "AM"

    else:
        period = "AM"

    newTime = str(hour) + ":" + min + " " + period
    return newTime

def to24hr(time):
    '''Converts 12 hour time back into 24 hour time

    Paramter:
        time (str): the 12 hour time as a string

    Returns:
        the original inputted time in 24 hour time'''

    t, period = time.split()[0], time.split()[1]
    hour = int(t[0])
    min = t[2:]
    if period == "PM":
        hour += 12

    elif hour < 10:
        hour = "0" + str(hour)

    newTime = str(hour) + ":" + min
    return newTime

def check_pwd(pwd):
    '''Checks if the password entered by the user meets
    the requirements of being at least 8 characters long, contains
    at least one uppercase letter, one lowercase letter, one digit, and one special character.

    Parameters:
        pwd (str): the password entered by the user

    Returns:
        bool: True if the password meets the requirements, False otherwise'''

    check = None
    if len(pwd) < 8:
        check = False
    elif not any(char.isupper() for char in pwd):
        check = False
    elif not any(char.islower() for char in pwd):
        check = False
    elif not any(char.isdigit() for char in pwd):
        check = False
    elif not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in pwd):
        check = False
    else:
        check = True

    return check

def check_email(email):
    '''Checks if the email entered by the user is in a valid format

    Parameters:
        email (str): the email address entered by the user

    Returns:
        bool: True if the email is in a valid format, False otherwise'''

    if "@" in email and "." in email and len(email) > 5:
        return True
    else:
        return False

def add_admins():
    '''Hard code admins account into the database when the app is first launched, only needs to be called once after init_db is called

    Parameters:
        None

    Returns:
        None '''
    db = get_db()
    db.execute('INSERT INTO users (first_name, last_name, email, phone_number, password, type)' \
    'VALUES ("Jake", "Kougan", "jakekougan6@gmail.com", "312-718-1065", ?, "1");', [generate_password_hash(os.getenv("ADMIN_PWD"), salt_length=11)])
    db.commit()
    print("Admin Accounts Ready for use!")

@app.cli.command('add_admins')
def add_admins_cmd():
    '''Allows the admin accounts to be added from the command line
    Enter python -m flask add_admins

    Parameters:
        None

    Returns:
        None'''
    add_admins()













