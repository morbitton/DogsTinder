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


conn = connect_db('localhost', 'root', 'LoginPass@@12', 'DogsTinder')


@app.route('/')
def index():
    return render_template('/DogTinder- index.html')


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
        # if authenticate_user(username, password):
        session["USERNAME"] = username
        session["PASSWORD"] = password
        return redirect(url_for('homepage'))
    return render_template('/register.html')


@app.route('/')
def home():
    return render_template('/home.html')


# def authenticate_user(username, password):
#     if check_username(username, password):
#         return True
#     return False


if __name__ == '__main__':
    app.run(host='0.0.0.0')