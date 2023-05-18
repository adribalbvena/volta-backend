import datetime
import requests
from flask import Flask, jsonify, request, session, abort
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from config import Config
from models import db, User, Trip, Activity, Plan
from dotenv import load_dotenv
import os
from utils import create_uuid

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

server_session = Session(app)
bcrypt = Bcrypt(app)
# CORS(app, supports_credentials=True)
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
    new_user = User(id=create_uuid(),
                    email=email,
                    password=encrypted_password)  # then, we pass the received parameters
    db.session.add(new_user)  # and then we add the new user to our db
    db.session.commit()  # and kinda 'execute' those changes with commit

    session["user_id"] = new_user.id

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
    print(session.get('user_id'))

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
@app.route('/users/trips', methods=["GET"])
def get_trips():
    # if "user_id" not in session:
    #     abort(401, "Unauthorized")
    user_session_id = session.get('user_id')
    print(user_session_id)
    user = db.session.get(User, user_session_id)
    if user is None:
        abort(404, description='User not found')

    trips = Trip.query.filter_by(user_id=user_session_id).order_by(Trip.creation_date.desc()).all()

    # Serialize the trips to JSON format
    trips_json = [trip.serialize() for trip in trips]

    # Return the serialized trips as a JSON response
    response = jsonify(trips_json)
    # response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response, 200


# ENDPOINT: '/delete_trip' this endpoint deletes a user trip from our database
@app.route('/user/trips/<trip_id>', methods=['DELETE'])  # this is wrong bs u can delete any trip of any user
def delete_trip(trip_id):
    trip = Trip.query.get(trip_id)
    if trip is None:
        abort(404, description='Trip not found')

    user_session_id = session.get('user_id')
    if trip.user.id != user_session_id:
        abort(403, description='You are not authorized to delete this trip')

    db.session.delete(trip)
    db.session.commit()

    return jsonify({'message': 'Trip and associated data deleted successfully'}), 200


# ENDPOINT: '/add_trip' this endpoint adds a user trip to our database
@app.route('/users/trips', methods=['POST'])
def add_trip():
    user_session_id = session.get('user_id')
    user = User.query.get(user_session_id)
    if user is None:
        abort(404, description='User not found')

    # Get the necessary data from the request
    destination = request.json.get('destination')
    start_date = datetime.datetime.strptime(request.json.get('start_date'), '%d/%m/%Y')
    end_date = datetime.datetime.strptime(request.json.get('end_date'), '%d/%m/%Y')

    # Create a new trip object and add it to the user's trips
    trip = Trip(id=create_uuid(), destination=destination, start_date=start_date, end_date=end_date)
    user.trips.append(trip)

    # Save the changes to the database
    db.session.add(trip)
    db.session.commit()

    # Return a response with the newly created trip object
    return jsonify(trip.serialize()), 201


# ENDPOINT: '/add_plan' this endpoint adds the plan to a user trip and then store it to database,
# like add the plan to favorites but the favorite is inside the list of trips... is not an easy task tbh xd
@app.route('/trips/<trip_id>/plans', methods=['POST'])
def add_plan(trip_id):
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        abort(404, description='Trip not found')

    data = request.get_json()
    if not data:
        abort(400, description='No data provided.')

    day_number = data.get('day')
    activities = data.get('activities')

    if not day_number:
        abort(400, description='Day number is required.')

    plan = Plan(id=create_uuid(), day_number=day_number, trip_id=trip_id)
    db.session.add(plan)

    if activities:
        for activity_data in activities:
            hour = activity_data.get('time')
            description = activity_data.get('description')

            if not hour:
                abort(400, description='Hour is required for each activity.')

            activity = Activity(id=create_uuid(), hour=hour, description=description, plan_id=plan.id)
            db.session.add(activity)

    db.session.commit()

    return jsonify({'message': 'Plan added successfully.'}), 201


@app.route("/trips/<trip_id>/plan", methods=["GET"])
def get_plan_from_db(trip_id):
    trip = Trip.query.get(trip_id)
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    plan = []
    for plan_entry in trip.plans:
        day_activities = {
            "day": plan_entry.day_number,
            "activities": []
        }
        for activity in plan_entry.activities:
            day_activities["activities"].append({
                "time": activity.hour,
                "description": activity.description
            })
        plan.insert(0, day_activities)

    return jsonify({"plan": plan})


# TEST: create a py file named 'test' and create the structure for the test (same as in the course, as we already did)

@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id", None)  # this is to remove the user_id key from the session, and set its value to None
    return {"message": "Logged out successfully"}, 200


if __name__ == '__main__':
    app.run(debug=True, port=8080)
