from app import db, login_manager
from flask_login import UserMixin, LoginManager

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(140))
    gallery = db.Column(db.String())
    count = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Gallery {}>'.format(self.body)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    login = db.Column(db.String(64), index=True, unique=False)
    fullname = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    picture = db.Column(db.String(120), index=True, unique=False)
    commentary = db.Column(db.String(120), index=True, unique=False)
    #gallery = db.relationship('Gallery', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

