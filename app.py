#!/usr/bin/env python3
from flask import Flask, render_template, request, session, redirect, url_for, flash
import logging
from flask_debugtoolbar import DebugToolbarExtension
from mysql import connector
from passlib.hash import sha256_crypt
# from flask_login import login_required, logout_user, current_user, login_user
# from .forms import LoginForm, SignupForm
# from .models import db, User
# from . import login_manager

app = Flask(__name__)

# !--- For debugging switch to true ---!
app.debug = False

app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
toolbar = DebugToolbarExtension(app)


def definedlog(fileHandler):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler(fileHandler)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def connect_db(host, user, password, database):
    connection = connector.connect(
        user=user, password=password, host=host, database=database)
    return connection


conn = connect_db('localhost', 'hadaran', '', 'DogsTinder')


@app.route('/')
def index():
    return render_template('/index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userDetails = request.form
        username = userDetails['username']
        password = sha256_crypt.encrypt(userDetails["password"])
        firstName = userDetails['firstName']
        lastName = userDetails['lastName']
        phone = userDetails['phone']
        email = userDetails['email']
        mycursor = conn.cursor()
        sql = "INSERT INTO users (username, password, firstName, lastName, phone, email) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (username, password, firstName, lastName, phone, email)
        mycursor.execute(sql, val)
        conn.commit()
        if authenticate_user(username, password):
            session["USERNAME"] = username
            session["PASSWORD"] = password
        return redirect(url_for('homepage'))
    return render_template('/register.html')


@app.route('/')
def home():
    return render_template('/home.html')


@app.route('/help')
def help():
    return render_template('/help.html')


def check_username(username, pas):
    maulers = conn.cursor()
    Fender = "SELECT * FROM users"
    maulers.execute(Fender)
    result = maulers.fetchall()
    for user in result:
        print(user)
        if user[0] == username:
            if sha256_crypt.verify(pas, user[1]):
                return True
    return False


def authenticate_user(username, password):
    if check_username(username, password):
        return True
    return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = req.get("password")
        if authenticate_user(username, password):
            session["USERNAME"] = username
            session["PASSWORD"] = password
            return redirect(url_for('homepage'))
        else:
            return redirect(url_for('login'))
        return render_template('homepage.html',
                               username=session["USERNAME"])
    return render_template('/register.html')


@app.route('/log_out')
def log_out():
    session.clear()
    return render_template('homepage.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')