from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()  # this is a common line of code used when working with the SQLAlchemy library,
# which is an Object Relational Mapper (ORM) for working with databases
# This line of code creates a new instance of the SQLAlchemy class and assigns it to the variable db.
# This instance can then be used to interact with a database, such as creating tables,
# inserting data, querying data, etc.



def create_uuid():
    """This uses uuid python module to return a Universally Unique IDentifier
    which is a 36-character alphanumeric string that can be used to identify tables"""
    return uuid4().hex


#  A model is something like the 'schema' of what our object
#  (which we will be storing in our database) is going to look like
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=create_uuid())
    email = db.Column(db.String(250), unique=True)  # is unique bc one user cannot have the same email as another user
    password = db.Column(db.Text, nullable=False)
    trips = db.relationship('Trip')


class Trip(db.Model):
    __tablename__ = "trips"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=create_uuid())
    destination = db.Column(db.String(70))
    startDate = db.Column(db.DateTime())
    endDate = db.Column(db.DateTime())
    user_id = db.Column(db.String(32), db.ForeignKey("users.id"))  # here we are saying that
    # one user can have many trips, and the trips are related to the user
    plans = db.relationship('Plan')


class Plan(db.Model):
    __tablename__ = "plan"
    day_number = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.String(32), db.ForeignKey("trips.id"))
    activities = db.relationship("Activity")


class Activity(db.Model):
    __tablename__ = "activities"
    hour = db.Column(db.String(50), primary_key=True)
    description = db.Column(db.Text)
    day_number = db.Column(db.Integer, db.ForeignKey("plan.day_number"))
