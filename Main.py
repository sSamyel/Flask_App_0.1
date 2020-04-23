from flask import Flask, Response, url_for, render_template, redirect, request, session, abort, flash
from flask_login import login_required, login_user, logout_user, LoginManager, UserMixin
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from flask_wtf import FlaskForm
import requests
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

app = Flask("main")
login_manager = LoginManager()
login_manager.init_app(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

NUM_USER = 0
Users = []
username = ""
origin = ""
tmail=""
tname = ""
error =""

commentary = "Добро пожаловать!"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    login = db.Column(db.String(64), index=True, unique=False)
    fullname = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    picture = db.Column(db.String(120), index=True, unique=False)
    commentary = db.Column(db.String(120), index=True, unique=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))



class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')

    def validate_username(self, username):
        global error
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            error = "yes"

    def validate_password(self, password):
        global error
        user = User.query.filter_by(password_hash=password.data).first()
        if error == "yes":
            error = "no"
            raise ValidationError('Не верный логин или пароль')
        else:
            error = "no"
            if user is None:
                raise ValidationError('Не верный логин или пароль')

class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    login = StringField('Имя', validators=[DataRequired()])
    fullname = StringField('Фамилия', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        global error
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пользователь с таким логином уже существует')


    def validate_email(self, email):
        global error
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пользователь с таким email уже существует')

class SettingForm(FlaskForm):
    username = StringField('Логин', validators=[])
    password = PasswordField('Пароль')
    login = StringField('Имя')
    fullname = StringField('Фамилия')
    email = StringField('Email', validators=[])
    file_object = FileField('file')
    commentary = StringField('Комментарий', validators=[Length(max=17)])
    submit = SubmitField('Внести изменения')


    def validate_username(self, username):
        if username.data != origin:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Пользователь с таким именем уже существует')

    def validate_email(self, email):
        if email.data != "" and email.data != tmail:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Пользователь с таким email уже существует')



class FileForm(FlaskForm):
    file_object = FileField('file', validators=[FileRequired()])
    submit = SubmitField('Загрузить')



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
    global NUM_USER
    global username
    global commentary, tname, tmail
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
                return render_template("mainPage.html", username=usname, commentary=commentary, login=tname, form=form)
    logout_user()
    return render_template("login.html", form=form)


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
        return render_template("mainPage.html", username = username, commentary=commentary,login=tname, form=form)
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
                f.save(app.root_path + '/files/' + f.filename)
                db.session.commit()
                #u.set_picture(fname)
            return render_template("profile.html", name=name, fullname=fullname, login=login, email=email, fname=fname, form=form )
    return redirect('/login')


@app.route("/logout")
@login_required
def logout():
    global username
    global tname
    global commentary
    logout_user()
    username = ""
    tname = ""
    commentary = "Добро пожаловать!"
    return redirect('/login')

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    global username
    global commentary
    global origin
    global tname
    global tmail
    origin = username
    users = User.query.all()
    for u in users:
        if u.username == username:
            form = SettingForm()
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
                print("fdsfd")
                return redirect('/profile')
            return render_template('setting.html', form=form)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = FileForm()
    if form.validate_on_submit():
        f = form.file_object.data
        print(app.root_path + '/files/' + f.filename)
        f.save(app.root_path + '/files/' + f.filename)
        return redirect('/index')
    else:
        return render_template('upload.html', form=form)

app.run(port=8008, host='127.0.0.1')

