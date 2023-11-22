import random
import hashlib
import db
import sqlite3
import flask
from flask import Flask, render_template, request, session, redirect
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
        host = request.host_url;

        wwws = cursor.execute('''SELECT * from links INNER JOIN links_types ON links.link_type_id = links_types.id WHERE user_id = ?''', (session['user_id'], )).fetchall()
        menu = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
        return render_template('profile.html', title="Профиль", menu=menu, user=user, wwws=wwws, host=host)


@app.route('/check', methods=['POST'])
def check():
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    user = cursor.execute('''SELECT * from users where login = ? ''', (request.form['login'],)).fetchone()
    hash = hashlib.md5(request.form['password'].encode())
    password = hash.hexdigest()
    login = request.form['login']
    if user != None:
        if password==user[2] and login == user[1]:
            print(session['www_id'])
            session['user_id'] = user[0]
            session['user_login'] = user[1]
            if 'www_id' in session and session['www_id']!=None:
                www = cursor.execute('''SELECT * from links where id = ? ''', (session['www_id'], )).fetchone()

                if www[4]==2:
                    session['www_id'] = None

                    count = www[5]+1

                    cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (count, www[0]))
                    connect.commit()
                    return redirect(www[1])
                else:
                    if www[3]==user[0]:
                        session['www_id'] = None
                        count = int(www[5])+1

                        cursor.execute('''UPDATE links SET count = ? WHERE id= ? ''', (count, www[0]))
                        connect.commit()
                        return redirect(www[1])
                    else:

                        return 'Нет доступа'

            else:

                session['user_id'] = user[0]
                session['user_login'] = user[1]

                host = request.host_url;

                wwws = cursor.execute('''SELECT * from links INNER JOIN links_types ON links.link_type_id = links_types.id WHERE user_id = ?''', (session['user_id'], )).fetchall()
                menu = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
                return redirect("/profile", code= 302)
        else:
            return ('Не верный пароль')
    else:
        return ('Такого пользователя нет')

@app.route("/")
def index():
    session['www_id'] = None
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    tipes = cursor.execute('''SELECT * from links_types  ''').fetchall()

    if 'user_login' in session and session['user_login'] != None:
        menu = [ {"name": "Главная", "url": "/"}, {"name": 'Профиль', "url": "profile"},]
    else:
        session['user_login'] = None
        menu = [{"name": "Главная", "url": "/"}, {"name": "Авторизация", "url": "auth"},{"name": "Регистрация", "url": "registration"}]
    return render_template('index.html', title="Главная", menu=menu, tipes=tipes)

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
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    host = request.host_url;
    user = cursor.execute('''SELECT * from users where id = ? ''', (session['user_id'], )).fetchone()
    wwws = cursor.execute('''SELECT * from links INNER JOIN links_types ON links.link_type_id = links_types.id WHERE user_id = ?''', (session['user_id'], )).fetchall()

    menu = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
    return render_template('profile.html', title="Профиль", menu=menu, user=user, wwws=wwws, host=host)



@app.route("/delete", methods=['POST'])
def delete():
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute('''DELETE from links where id = ? ''', (request.form['id'], ))
    connect.commit()
    user = cursor.execute('''SELECT * from users where id = ? ''', (session['user_id'], )).fetchone()


    wwws = cursor.execute('''SELECT * from links INNER JOIN links_types ON links.link_type_id = links_types.id WHERE user_id = ?''', (session['user_id'], )).fetchall()
    menu = [{"name": "Главная", "url": "/"},{"name": 'Профиль', "url": "profile"},]
    return render_template('profile.html', title="Профиль", menu=menu, user=user, wwws=wwws)




@app.route("/update", methods=['POST'])
def update():
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()
    www = cursor.execute('''SELECT id, hreflink from links where id = ? ''', (request.form['id'], )).fetchone()

    types = cursor.execute('''SELECT * from links_types ''').fetchall()

    return render_template('update.html', title="Профиль", menu=menu, www=www, types=types)


@app.route("/saveupdate", methods=['POST'])
def saveupdate():
    connect = sqlite3.connect('db.db', check_same_thread=False)
    cursor = connect.cursor()



    if request.form['namewww'] == '':
        name = hashlib.md5(request.form['namewww'].encode()).hexdigest()[:random.randint(8, 12)]
    else:
        name_in_base = cursor.execute('''SELECT * from links where hreflink = ?''', (request.form['namewww'],)).fetchone()
        if name_in_base!=None:
            print(name_in_base[0])
            print(request.form['idwww'])
            if int(name_in_base[0])==int(request.form['idwww']):
                name = request.form['namewww']
            else:

                name = hashlib.md5(request.form['namewww'].encode()).hexdigest()[:random.randint(8, 12)]
        else:
            name = request.form['namewww']



    if (request.form['type'] == "0"):
        cursor.execute('''UPDATE links SET hreflink = ? WHERE id=?''', (name, request.form['idwww']))
        connect.commit()
    else:
        cursor.execute('''UPDATE links SET hreflink = ?, link_type_id = ? WHERE id=?''', (name, request.form['type'], request.form['idwww']))
        connect.commit()

    host = request.host_url;
    user = cursor.execute('''SELECT * from users where id = ? ''', (session['user_id'],)).fetchone()
    wwws = cursor.execute(
        '''SELECT * from links INNER JOIN links_types ON links.link_type_id = links_types.id WHERE user_id = ?''',
        (session['user_id'],)).fetchall()

    menu = [{"name": "Главная", "url": "/"}, {"name": 'Профиль', "url": "profile"}, ]
    return render_template('profile.html', title="Профиль", menu=menu, user=user, wwws=wwws, host=host)



@app.route("/reduce", methods=['POST'])
def short():
    if 'user_login' in session and session['user_login'] !=None:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": 'Профиль', "url": "profile"},
        ]
    else:
        menu = [
            {"name": "Главная", "url": "/"},
            {"name": "Авторизация", "url": "auth"},
            {"name": "Регистрация", "url": "reg"}
        ]


    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()


    tipes = cursor.execute('''SELECT * from links_types  ''').fetchall()

    links = cursor.execute('''SELECT * FROM links where link = ? AND user_id = ?''', (request.form['www'],session.get('user_id'))).fetchall()

    if links == []:
        if request.form['namewww'] != '':
            namewww = cursor.execute('''select * from links where hreflink=?''', (request.form['namewww'],)).fetchone()


            if namewww == None:
                user_address = request.form['namewww']
            else:
                user_address = hashlib.md5(request.form['www'].encode()).hexdigest()[:random.randint(8, 12)]
        else:
            user_address = hashlib.md5(request.form['www'].encode()).hexdigest()[:random.randint(8, 12)]

        namehash = cursor.execute('''SELECT * FROM links where hreflink=?''', (user_address,)).fetchone()

        if namehash !=None:
            user_address = hashlib.md5(user_address.encode()).hexdigest()[:random.randint(8, 12)]


        if request.form['types']=='1':
            if ('user_id' in session and session['user_id']!=None):


                cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['www'], user_address, session['user_id'], request.form['types'],0))
                connect.commit()
                donewww = request.host_url + 'www/' + user_address

                flask.flash(f'{donewww}')
                return render_template('index.html', title="Главная", menu=menu, tipes=tipes)
            else:

                cursor.execute('''INSERT INTO links('link', 'hreflink', 'link_type_id', 'count') VALUES(?, ?, ?, ?)''', (request.form['www'], user_address, request.form['types'], 0))
                connect.commit()
                donewww = request.host_url + 'www/' + user_address

                flask.flash(f'{donewww}')
                return render_template('index.html', title="Главная", menu=menu, tipes=tipes)

        elif request.form['types']=='2':


            cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['www'], user_address, session['user_id'], request.form['types'], 0))
            connect.commit()
            donewww = request.host_url + 'www/' + user_address

            flask.flash(f'{donewww}')
            return render_template('index.html', title="Главная", menu=menu, tipes=tipes)
        else:

            cursor.execute('''INSERT INTO links('link', 'hreflink', 'user_id', 'link_type_id', 'count') VALUES(?, ?, ?, ?, ?)''',(request.form['www'], user_address, session['user_id'], request.form['types'], 0))
            connect.commit()
            donewww = request.host_url + 'www/' + user_address

            flask.flash(f'{donewww}')
            return render_template('index.html', title="Главная", menu=menu, tipes=tipes)
    else:
        donewww = 'такая ссылка у вас уже есть'

        flask.flash(f'{donewww}')
        return render_template('index.html', title="Главная", menu=menu, tipes=tipes)



@app.route("/error")
def error():
    return render_template('error.html', title="Ошибка", menu=menu)

@app.route("/www/<wwwstep>")
def step(wwwstep):
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    www = cursor.execute('''SELECT * FROM links INNER JOIN links_types ON links_types.id = links.link_type_id WHERE hreflink = ?''', (wwwstep, ) ).fetchone()

    print (www)

    if www == None:
        return redirect('/error')
    else:
        if www[6]==1:
            cursor.execute('''UPDATE links SET count = ? WHERE id=?''',(www[5]+1, www[0]))
            connect.commit()
            return redirect(www[1])
        elif www[6]==2:
            if 'user_id' in session and session['user_id']!=None:
                cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (www[5] + 1, www[0]))
                connect.commit()
                return redirect(www[1])
            else:
                session['www_id'] = www[0]
                menu = [
                    {"name": "Авторизация", "url": "auth"},
                    {"name": "Регистрация", "url": "reg"}
                ]
                return render_template('auth.html', title="Авторизация", menu=menu)

        elif www[6]==3:
            if 'user_id' in session and session['user_id'] != None:
                if (www[3]==session['user_id']):
                    cursor.execute('''UPDATE links SET count = ? WHERE id=?''', (www[5] + 1, www[0]))
                    connect.commit()
                    return redirect(f"{www[1]}")
                else:
                    return ('Нет доступа')
            else:
                session['www_id'] = www[0]
                menu = [
                    {"name": "Авторизация", "url": "auth"},
                    {"name": "Регистрация", "url": "reg"}
                ]
                return render_template('auth.html', title="Авторизация", menu=menu)




if __name__=='__main__':
    app.run(debug=True)
