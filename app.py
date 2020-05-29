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

UPLOAD_FOLDER = os.path.abspath(os.curdir) + 'static/images'

app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
#toolbar = DebugToolbarExtension(app)


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


# Connect to the database
connection = pymysql.connect("localhost", "root", "LoginPass@@12", "DogsTinder")
mycursor = connection.cursor()


@app.route('/')
def index():
    return render_template('/index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    mycursor = connection.cursor()
    message = ""
    if request.method == 'POST':
        try:
            userDetails = request.form
            username = userDetails['username']
            unQuery = "SELECT username FROM users WHERE username = '" + username + "'"
            mycursor.execute(unQuery)
            username_from_db = mycursor.fetchall()
            if username_from_db:
                raise Exception('User name already Exists!')
            password = userDetails["password1"]
            password_confirm = userDetails["password2"]
            if password != password_confirm:
                raise Exception('Passwords does not match!')
            password = sha256_crypt.encrypt(userDetails["password1"])
            firstName = userDetails['firstName']
            lastName = userDetails['lastName']
            phone = userDetails['phone']
            email = userDetails['email']
            mycursor = connection.cursor()
            sql = "INSERT INTO users (username, password, firstName, lastName, phone, email) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (username, password, firstName, lastName, phone, email)
            mycursor.execute(sql, val)
            connection.commit()
            session['USERNAME'] = username
            return redirect(url_for('homepage'))
        except Exception as error:
            message = str(error)

    return render_template('/register.html', message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if get_user_logged_in():
        return redirect('homepage')

    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = req.get("password")
        try:
            authenticate_user(username, password)
            return redirect(url_for('homepage'))
        except Exception as error:
            message = str(error)
    return render_template('/login.html', message=message)


def authenticate_user(username, password):
    maulers = connection.cursor()
    Fender = "SELECT username, password FROM users WHERE username = '" + username + "'"
    maulers.execute(Fender)
    result = maulers.fetchall()
    print(result)
    for user in result:
        if sha256_crypt.verify(password, user[1]):
            session["USERNAME"] = user[0]
            return True
        else:
            raise Exception("Password doesn't match")
    raise Exception("Username not found")


def get_user_logged_in():
    if "USERNAME" in session:
        return session["USERNAME"]
    return False


@app.route("/homepage", methods=['POST', 'GET'])
def homepage():
    un = get_user_logged_in()
    if un:
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
        queryhomepage = "SELECT * FROM dogs"

        # add query for excluding from likes table
        queryhomepage += " WHERE dog_id NOT IN (SELECT dog_id FROM likes WHERE username='" + un + "')"

        # add query for the filter in homepage
        if filter != "":
            queryhomepage += " AND " + filter

        mycursor.execute(queryhomepage)
        result = mycursor.fetchall()
        return render_template('homepage.html', dogs=result)
    return redirect('login')


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


@app.route('/create_dog_profile/', methods=['POST', 'GET'])
def create_dog_profile():
    username = get_user_logged_in()
    if username:
        if request.method == "POST":
            try:
                details = request.form
                name = details['dog_name']

                # check if chip already exists
                chip = details['chip_number']
                mycursor.execute("SELECT dog_id FROM dogs WHERE dog_id = '" + chip + "'")
                chip_from_db = mycursor.fetchall()
                if (chip_from_db):
                    raise Exception('Chip already Exists!')

                birth_date = details['birth_date']
                gender = details['gender']
                area = details['area']
                city = details['city']
                type = details['type']
                description = details['description']
                img1 = request.files['files']
                path1 = os.path.join('images/', img1.filename)
                img1.save(os.path.join(UPLOAD_FOLDER, img1.filename))
                photo1 = convertToBinaryData(
                    os.path.join(UPLOAD_FOLDER, img1.filename))
                img2 = request.files['img2']
                if img2.filename != '':
                    img2.save(os.path.join(UPLOAD_FOLDER, img2.filename))
                    path2 = os.path.join('images/', img2.filename)
                    photo2 = convertToBinaryData(
                        os.path.join(UPLOAD_FOLDER, img2.filename))
                else:
                    photo2 = ''
                    path2 = ''
                img3 = request.files['img3']
                if img3.filename != '':
                    path3 = os.path.join('images/', img3.filename)
                    img3.save(os.path.join(UPLOAD_FOLDER, img3.filename))
                    photo3 = convertToBinaryData(
                        os.path.join(UPLOAD_FOLDER, img3.filename))
                else:
                    photo3 = ''
                    path3 = ''

                mycursor.execute(
                    "INSERT INTO dogs(dog_id,name,bday,gender,area,city, type,details,pic1,path1,pic2,path2,pic3,path3,username) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (chip, name, birth_date, gender, area, city, type, description, photo1, path1, photo2, path2, photo3, path3,
                    username))
                connection.commit()
                message = "Dog added successfully"
            except Exception as error:
                message = str(error)
        else:
            message = " "

        return render_template('create_dog_profile.html', message=message)
    return redirect('/login')


@app.route("/dogProfile/<dog_id>")
def dogProfile(dog_id):
    uname = get_user_logged_in()
    if uname:
        queryDogProfile = "select * from dogs where dog_id=" + dog_id
        mycursor.execute(queryDogProfile)
        result = mycursor.fetchall()
        return render_template('dogProfile.html', dog=result)
    return redirect('login')


@app.route("/favorites/add", methods=['POST'])
def yes_button():
    username = get_user_logged_in()
    if username:
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


@app.route("/favorites/", methods=['POST', 'GET'])
def favorites():
    username = get_user_logged_in()
    if username:
        if request.method == 'POST':
            details = request.form
            clear_but = details['clear']
            if clear_but == 'yes':
                clearChoices(username)
                return redirect('/homepage')
        query_favorites = "select * from dogs left join likes on likes.dog_id = dogs.dog_id where likes.username='" + \
            username + "' AND answer='yes'"
        mycursor.execute(query_favorites)
        dogs = mycursor.fetchall()
        connection.commit()
        return render_template('favorites.html', dogs=dogs)
    return redirect('/login')


def clearChoices(username):
    queryClear = "DELETE FROM likes WHERE username='" + username + "'"
    mycursor.execute(queryClear)
    connection.commit()


# def connect_db(host, user, password, database):
#     connection = connector.connect(
#         user=user, password=password, host=host, database=database)
#     return connection


@app.route('/help')
def help():
    uname = get_user_logged_in()
    if uname:
        return render_template('/help.html')
    return redirect('login')


@app.route('/updateUser', methods=['POST', 'GET'])
def updateUser():
    uname = get_user_logged_in()
    if uname:
        mycursor.execute(
            "SELECT * FROM users WHERE username = '" + uname + "'")
        user = mycursor.fetchall()
        if request.method == 'POST':
            formDetails = request.form
            name = formDetails['name']
            if name != "":
                sql = "UPDATE users SET first_name = '" + \
                    name + "'  WHERE username = '" + uname + "'"
                mycursor.execute(sql)
                connection.commit()

            lastname = formDetails['lastname']
            if lastname != "":
                sql = "UPDATE users SET last_name = '" + \
                    lastname + "'  WHERE username = '" + uname + "'"
                mycursor.execute(sql)
                connection.commit()

            phone = formDetails["tel"]
            if phone != "":
                sql = "UPDATE users SET phone = '" + phone + \
                    "'  WHERE username = '" + uname + "'"
                mycursor.execute(sql)
                connection.commit()

            mail = formDetails['mail']
            if mail != "":
                sql = "UPDATE users SET email = '" + mail + \
                    "'  WHERE username = '" + uname + "'"
                mycursor.execute(sql)
                connection.commit()

            newpass = formDetails["newpass"]
            renewpass = formDetails["confirm"]

            if (newpass != "") & (renewpass != ""):
                if newpass == renewpass:
                    newpass = sha256_crypt.encrypt(newpass)
                    renewpass = sha256_crypt.encrypt(renewpass)
                    sql = "UPDATE users SET password='" + newpass + "', repassword='" + \
                        renewpass + "' where username='" + uname + "'"
                    mycursor.execute(sql)
                    connection.commit()

            message = "your details were updates successfully"
            mycursor.execute(
                "SELECT * FROM users WHERE username = '" + uname + "'")
            user = mycursor.fetchall()
        else:
            message = ""

        return render_template("updateUser.html", dogs=showDogs(), user=user, m=message)
    return redirect('login')


def showDogs():
    un = session["USERNAME"]
    queryShowDogs = "select dog_id,name from dogs where username='" + un + "'"
    mycursor.execute(queryShowDogs)
    result = mycursor.fetchall()
    return result


@app.route("/updateUser/<dog_id>", methods=['POST', 'GET'])
def updateDog(dog_id):
    if request.method == 'POST':
        formDetails = request.form
        if 'delete' in formDetails:
            deleteDog(dog_id)
        elif 'adopt' in formDetails:
            adopted(dog_id)
    return redirect('/updateUser')


def deleteDog(dog_id):
    queryDeleteDog = "DELETE FROM dogs WHERE dog_id =" + dog_id
    mycursor.execute(queryDeleteDog)
    connection.commit()
    return True


def adopted(dog_id):
    mycursor.execute(
        "INSERT INTO adopted SELECT d.* FROM dogs AS d WHERE dog_id = " + dog_id)
    connection.commit()
    deleteDog(dog_id)
    return True


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
     app.run(host='0.0.0.0', debug=True)
