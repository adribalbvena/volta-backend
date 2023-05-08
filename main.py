from flask import Flask, jsonify, request, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

server_session = Session(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
db.init_app(app)

with app.app_context():
    db.create_all()


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
    new_user = User(email=email, password=encrypted_password)  # then, we pass the received parameter email and the encrypted password
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


@app.route('/@current_user')
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


if __name__ == '__main__':
    app.run(debug=True, port=8080)
