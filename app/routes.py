from datetime import datetime
from flask import render_template, redirect
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.forms import LoginForm, RegistrationForm, SettingForm, FileForm
from app.models import User



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/mainPage', methods=['GET','POST'])
def index():
    a = render_template('mainPage.html', username = username, commentary = commentary, login = tname)
    return a

@app.route('/main')
def main():
    return redirect('/mainPage')

@app.route('/login', methods=['GET','POST'])
def login():
    global username,commentary, tname, tmail
    form = LoginForm()
    #users = User.query.all()
    #for u in users:
        #db.session.delete(u)
    #db.session.commit()
    if form.validate_on_submit():
        usname = form.username.data
        password = form.password.data
        users = User.query.all()
        for u in users:
            if usname == u.username and password == u.password_hash:
                login_user(u)
                username = usname
                commentary = u.commentary
                tname = u.login
                tmail = u.email
                return render_template("mainPage.html", username=current_user.username, commentary=current_user.commentary, login=current_user.login, form=form)
    logout_user()
    return render_template("login.html", form=form)

username = ""
origin = ""
tmail=""
tname = ""
commentary = "Добро пожаловать!"

@app.route('/registration', methods=['GET','POST'])
def registration():
    global NUM_USER
    global username
    global login, tname, tmail
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        login = form.login.data
        fullname = form.fullname.data
        email = form.email.data
        picture = "avatar.png"
        commentary = "Добро пожаловать!"
        user = User(username=username, password_hash=password, login=login, fullname=fullname, email=email, picture=picture, commentary=commentary)
        username = ""
        tname = ""
        tmail = ""
        db.session.add(user)
        db.session.commit()
        NUM_USER += 1
        return redirect('/mainPage')
    else:
        logout_user()
    return render_template("registration.html", form=form)

@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    global username
    users = User.query.all()
    for u in users:
        if u.username == username:
            name = u.username
            fullname = u.fullname
            login = u.login
            email = u.email
            form = FileForm()
            fname = u.picture
            if form.validate_on_submit():
                f = form.file_object.data
                fname = f.filename
                u.picture = f.filename
                db.session.commit()
            return render_template("profile.html", name=name, fullname=fullname, login=login, email=email, fname=fname, form=form )
    return redirect('/login')


@app.route("/logout")
@login_required
def logout():
    global commentary, tname, username
    logout_user()
    username = ""
    tname = ""
    commentary = "Добро пожаловать!"
    return redirect('/login')

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    global tmail, username, commentary, origin, tname
    origin = username
    users = User.query.all()
    for u in users:
        if u.username == username:
            form = SettingForm(current_user.username, current_user.email)
            if form.validate_on_submit():
                usernam = form.username.data
                password = form.password.data
                login = form.login.data
                fullname = form.fullname.data
                email = form.email.data
                picture = form.file_object.data
                commentar = form.commentary.data
                if commentar != "":
                   u.commentary = commentar
                   commentary = commentar
                if picture != None:
                   picture.save(app.root_path + '/static/' + picture.filename)
                   u.picture = picture.filename
                if email != "":
                   tmail = email
                   u.email = email
                if fullname != "":
                   u.fullname = fullname
                if login != "":
                   u.login = login
                   tname = login
                if usernam != "":
                   u.username = usernam
                   username = usernam
                if password != "":
                   u.password_hash = password
                db.session.commit()
                return redirect('/profile')
            return render_template('setting.html', form=form)


app.run(port=8080, host='127.0.0.1')