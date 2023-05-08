from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()


def create_uuid():
    """This uses uuid python module to return a Universally Unique IDentifier
    which is a 36-character alphanumeric string that can be used to identify tables"""
    return uuid4().hex


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=create_uuid())
    email = db.Column(db.String(250), unique=True)
    password = db.Column(db.Text, nullable=False)

# class Trip
