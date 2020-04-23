from app import db, login_manager
from flask_login import UserMixin, LoginManager



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