from flask_wtf.file import FileField, FileRequired
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User

error =""

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

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(SettingForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        super(SettingForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Пользователь с таким именем уже существует')



    def validate_email(self, email):
        if email.data != "" and email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Пользователь с таким email уже существует')



class FileForm(FlaskForm):
    file_object = FileField('file', validators=[FileRequired()])
    submit = SubmitField('Редактировать')

class EditorForm(FlaskForm):
    file_object = FileField('file', validators=[FileRequired()])
    submit = SubmitField('Загрузить')

class Editor2Form(FlaskForm):
    file_object = FileField('file', validators=[FileRequired()])
    submit = SubmitField('Загрузить')

class GalleryForm(FlaskForm):
    text = StringField('Текст')
    submit = SubmitField('Удалить')

class CutForm(FlaskForm):
    x = StringField('x')
    y = StringField('y')
    x1 = StringField('x1')
    y1 = StringField('y1')
    x2 = StringField('x2')
    y2 = StringField('y2')
    submitCut = SubmitField('Обрезать')

class RotateForm(FlaskForm):
    submitRotate = SubmitField('Повернуть')

class ResizeForm(FlaskForm):
    submitResize = SubmitField('Преобразовать')

class BrightForm(FlaskForm):
    submitBright = SubmitField('Изменить')

class ContrastForm(FlaskForm):
    submitContrast = SubmitField('Изменить')