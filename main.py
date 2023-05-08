import requests
from flask import Flask, jsonify, request, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from config import Config
from models import db, User, Trip, Activity, Plan
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

server_session = Session(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
db.init_app(app)

#  This method creates a new context application which is required to access certain Flask features
#  that are tied to the application context, such as the current application and request objects.
#  In this case, we need to create an application context to ensure that the database tables are created
#  within the context of our Flask application.
with app.app_context():
    db.create_all()  # this method is used to create all the tables that are defined in the database schema.


@app.route('/register', methods=["POST"])
def add_user():
    # Here we are getting the fields email and password
    email = request.json['email']
    password = request.json['password']

    # Here we are checking on our database if there is a user with this email already created
    is_user_existent = User.query.filter_by(email=email).first() is not None

    if is_user_existent:
        #  if the user already exists, then we return an error message and the 409 http code which is 'conflict'
        return jsonify({'error': 'User already registered'}), 409

    # and if the user does not exist yet, then we create a new one
    encrypted_password = bcrypt.generate_password_hash(password)  # first, we use bcrypt to encrypt the password
    new_user = User(email=email,
                    password=encrypted_password)  # then, we pass the received parameter email and the encrypted password
    db.session.add(new_user)  # and then we add the new user to our db
    db.session.commit()  # and kinda 'execute' those changes with commit

    return jsonify({
        'id': new_user.id,
        'email': new_user.email
    })


@app.route('/login', methods=["POST"])
def user_login():
    email = request.json['email']
    password = request.json['password']

    # Here we are querying our db to check if a user with that email exist
    user = User.query.filter_by(email=email).first()

    if user is None:
        # If the user does not exist, we throw an error message and the 401 http code which is 'unauthorized'
        return jsonify({'error': 'Unauthorized'}), 401

    # Here we are checking if the password provided match with the password in our db,
    # through bcrypt because is a hashed password
    if not bcrypt.check_password_hash(user.password, password):
        # if the passwords does not match then we throw an error message again
        return jsonify({'error': 'Unauthorized'}), 401

    session['user_id'] = user.id

    return jsonify({
        'id': user.id,
        'email': user.email
    })


@app.route('/@current_user', methods=["GET"])
def get_current_user():
    # if there is an invalid session this will return None
    user_authenticated_id = session.get('user_id')

    if not user_authenticated_id:
        return jsonify({'error': 'Unauthorized'}), 401

    # and if the session is valid, then will return the user that we are querying here by id
    user = User.query.filter_by(id=user_authenticated_id).first()
    return jsonify({
        'id': user.id,
        'email': user.email
    })




# Here we are getting the query params days and destination,
# example of endpoint: http://127.0.0.1:8080/get_plan?days=3&destination=London
@app.route('/get_plan', methods=["GET"])
def get_plan():
    args = request.args
    days = args.get('days')
    destination = args.get('destination')
    endpoint = 'https://ai-trip-planner.p.rapidapi.com/'
    params = {'days': days, 'destination': destination}
    headers = {'X-RapidAPI-Key': os.environ.get('PLAN_KEY'),
               'X-RapidAPI-Host': 'ai-trip-planner.p.rapidapi.com'}

    response = requests.get(endpoint, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({'error': 'Failed to get data from API'}), 500

# THINGS TO DO:
# ENDPOINT: '/get_trips' this endpoint will be returning the user trips stored in our database

# ENDPOINT: '/add_trip' this endpoint adds a user trip to our database

# ENDPOINT: '/delete_trip' this endpoint deletes a user trip from our database

# ENDPOINT: '/add_plan' this endpoint adds the plan to a user trip and then store it to database,
# like add the plan to favorites but the favorite is inside the list of trips... is not an easy task tbh xd

# TEST: create a py file named 'test' and create the structure for the test (same as in the course, as we already did)

if __name__ == '__main__':
    app.run(debug=True, port=8080)