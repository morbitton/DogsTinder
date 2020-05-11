import logging
import os
import pymysql
from flask import render_template, request, session, redirect, url_for, Flask
from mysql import connector
from passlib.hash import sha256_crypt

# from passlib.hash import sha256_crypt as sha256
# from flask_login import login_required, logout_user, current_user, login_user
# from forms import LoginForm, SignupForm
# from .models import db, User
# from . import login_manager

app = Flask(__name__)

# !--- For debugging switch to true ---!
app.debug = True

UPLOAD_FOLDER = 'DogsTinder/static/images/'

app = Flask(__name__)

# Connect to the database
connection = pymysql.connect("localhost", "root", "", "dogstinder")
mycursor = connection.cursor()


# app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
# toolbar = DebugToolbarExtension(app)

# mydb = pymysql.connect("localhost", "hadaran", "", "dogstinder")
# myCursor = mydb.cursor()
#
@app.route('/', methods=['POST', 'GET'])
@app.route("/homepage", methods=['POST', 'GET'])
def homepage():
    un = "mor"
    req = request.form
    filter = ""
    if request.method == 'POST':
        if req.get("filter") == 'submit':
            ge = req.get("gender")
            ar = req.get("area")
            if ge and ar:
                filter = "gender='" + ge + "' and area ='" + ar + "'"
            elif ge:
                filter = "gender='" + ge + "'"
            elif ar:
                filter = "area='" + ar + "'"
    else:
        queryhomepage = "SELECT * FROM dogs"

    # add query for excluding from likes table
    queryhomepage += " WHERE dog_id NOT IN (SELECT dog_id FROM likes WHERE username='" + un + "')"

    # add query for the filter in homepage
    if filter != "":
        queryhomepage += " AND " + filter

    mycursor.execute(queryhomepage)
    result = mycursor.fetchall()
    return render_template('homepage.html', dogs=result)


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


# @app.route('/', methods=['POST', 'GET'])
@app.route('/create_dog_profile/', methods=['POST', 'GET'])
def create_dog_profile():
    if request.method == "POST":
        details = request.form
        name = details['dog_name']
        chip = details['chip_number']
        birth_date = details['birth_date']
        gender = details['gender']
        area = details['area']
        city = details['city']
        type = details['type']
        description = details['description']
        img1 = request.files['files']
        path1 = os.path.join('images/', img1.filename)
        img1.save(os.path.join(UPLOAD_FOLDER, img1.filename))
        photo1 = convertToBinaryData(os.path.join(UPLOAD_FOLDER, img1.filename))
        img2 = request.files['img2']
        if img2.filename != '':
            img2.save(os.path.join(UPLOAD_FOLDER, img2.filename))
            path2 = os.path.join('images/', img2.filename)
            photo2 = convertToBinaryData(os.path.join(UPLOAD_FOLDER, img2.filename))
        else:
            photo2 = ''
            path2 = ''
        img3 = request.files['img3']
        if img3.filename != '':
            path3 = os.path.join('images/', img3.filename)
            img3.save(os.path.join(app.config['UPLOAD_FOLDER'], img3.filename))
            photo3 = convertToBinaryData(os.path.join(app.config['UPLOAD_FOLDER'], img3.filename))
        else:
            photo3 = ''
            path3 = ''

        username = "mor"

        mycursor.execute(
            "INSERT INTO dogs(dog_id,name,b_date,gender,area,city, type,details,pic1,path1,pic2,path2,pic3,path3,username) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (chip, name, birth_date, gender, area, city, type, description, photo1, path1, photo2, path2, photo3, path3,
             username))
        connection.commit()
        # mycursor.close()
    return render_template('create_dog_profile.html')

    return render_template('create_dog_profile.html')


@app.route("/dogProfile/<dog_id>")
def dogProfile(dog_id):
    queryDogProfile = "select * from dogs where dog_id=" + dog_id
    mycursor.execute(queryDogProfile)
    result = mycursor.fetchall()
    return render_template('dogProfile.html', dog=result)


@app.route("/favorites/add", methods=['POST'])
def yes_button():
    # if (is_user_logged_in()): # the function will check session of username
    username = "mor"
    details = request.form

    dog_id = details['dog_id']
    answer = details['answer']
    if answer == 'yes' or answer == 'no':
        mycursor.execute(
            "INSERT INTO likes VALUES (%s, %s,%s)",
            (username, dog_id, answer))

    connection.commit()

    return 'success'
    return 'fail'


@app.route("/favorites/" ,methods=['POST','GET'])
def favorites():
    username = "mor"
    if request.method == 'POST':
        details = request.form
        clear_but = details['clear']
        if clear_but == 'yes':
            clearChoices()
    query_favorites = "select * from dogs left join likes on likes.dog_id = dogs.dog_id where user_name='" + username + "' AND answer='yes'"
    mycursor.execute(query_favorites)
    dogs = mycursor.fetchall()
    connection.commit()
    # mycursor.close()
    return render_template('favorites.html', dogs=dogs)


def clearChoices():
    um = "mor"
    queryClear = "DELETE FROM likes WHERE user_name='" + um + "'"
    mycursor.execute(queryClear)
    connection.commit()
    return redirect(url_for('/homepage/'))


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


# def connect_db(host, user, password, database):
#     connection = connector.connect(
#         user=user, password=password, host=host, database=database)
#     return connection


# conn = connect_db('localhost', 'hadaran', '', 'DogsTinder')


@app.route('/index')
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
        mycursor = connection.cursor()
        sql = "INSERT INTO users (username, password, firstName, lastName, phone, email) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (username, password, firstName, lastName, phone, email)
        mycursor.execute(sql, val)
        connection.commit()
        if authenticate_user(username, password):
            session["USERNAME"] = username
            session["PASSWORD"] = password
        return redirect(url_for('homepage'))
    return render_template('/register.html')


# @app.route('/')
# def home():
#     return render_template('/home.html')


@app.route('/help')
def help():
    return render_template('/help.html')


def check_username(username, pas):
    maulers = connection.cursor()
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


# לעדכון פרופיל משתמש
# @app.route("/")
@app.route('/updateUser', methods=['GET', 'POST'])
def updateUser():
    if request.method == 'POST':
        formDetails = request.form
        uname = formDetails['username']
        name = formDetails['name']
        lastname = formDetails['lastname']
        tel = formDetails['tel']
        mail = formDetails['mail']
        oldpass = sha256_crypt.encrypt(formDetails["oldpass"])
        newpass = sha256_crypt.encrypt(formDetails["newpass"])
        renewpass = sha256_crypt.encrypt(formDetails["renewpass"])
        queryUpdateUser = "UPDATE users SET username=uname, password=newpass, phone=tel where username=uname"
        mycursor.execute(queryUpdateUser)
        connection.commit()
        return True;
    return True;


#
#   if authenticate_user(username, password):
#       session["USERNAME"] = username
#       session["PASSWORD"] = password
#   return redirect(url_for('homepage'))
# return render_template('/register.html')


@app.route('/log_out')
def log_out():
    session.clear()
    return render_template('homepage.html')


# if __name__ == '__main__':
#     app.run(host='0.0.0.0')


if __name__ == "__main__":
    app.run(debug=True)
