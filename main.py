import random
import hashlib
import db
import sqlite3
from flask import Flask, render_template, request, session
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required

app = Flask(__name__, template_folder='html', static_folder='html/static')
app.config["JWT_SECRET_KEY"]="youshallnotpass"
app.config['SECRET_KEY']='777'
menu = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "registration"}]

@app.route('/insert', methods=['POST'])
def insert():
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    login = cursor.execute('''SELECT * from users where login = ? ''', (request.form['login'], )).fetchall()
    print(login)
    if login!=[]:
        return 'Логин уже занят'
    else:
        hash = hashlib.md5(request.form['pass'].encode())
        password = hash.hexdigest()
        cursor.execute('''INSERT INTO users('login', 'password') VALUES(?, ?)''', (request.form['login'], password))
        connect.commit()
        user = cursor.execute('''SELECT * from users where login = ? ''', (request.form['login'],)).fetchone()
        session['user_id']  = user[0]
        session['user_login'] = user[1]
        if 'user_login' in session and session['user_login'] != None:
            menu = [{"name": "Главная", "url": "/"},{"name": session['user_login'], "url": "profile"},]
        else:
            menu = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "registration"}]
        return render_template('profile.html', title="Профиль", menu=menu)

@app.route('/check', methods=['POST'])
def check():
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    user = cursor.execute('''SELECT * from users where login = ? ''', (request.form['login'],)).fetchone()
    hash = hashlib.md5(request.form['password'].encode())
    password = hash.hexdigest()
    if password==user[2]:
        session['user_id'] = user[0]
        session['user_login'] = user[1]
        if 'user_login' in session and session['user_login'] != None:
            menu = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
        else:
            menu = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"}, {"name": "Регистрация", "url": "registration"}]
        return render_template('profile.html', title="Профиль", menu=menu)
    else:
        return ('Не верный пароль')

@app.route("/")
def index():
    if 'user_login' in session and session['user_login'] != None:
        menu = [ {"name": "Главная", "url": "/"}, {"name": 'Профиль', "url": "profile"},]
    else:
        menu = [{"name": "Главная", "url": "/"}, {"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "registration"}]
    return render_template('index.html', title="Главная", menu=menu)

@app.route('/logout', methods=['POST'])
def logout():
    session['user_id'] = None
    session['user_login'] = None
    return render_template('index.html', title="Главная", menu=menu)

@app.route("/auth")
def auth():
    return render_template('auth.html', title="Авторизация", menu=menu)

@app.route("/registration")
def reg():
    menu = [{"name": "Главная", "url": "/"},{"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "registration"}]
    return render_template('registration.html', title="Регистрация", menu=menu)

@app.route("/profile")
def profile():
    menu = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
    return render_template('profile.html', title="Профиль", menu=menu)

if __name__=='__main__':
    app.run(debug=True)
