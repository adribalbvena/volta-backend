from dotenv import load_dotenv
import os
import redis

load_dotenv()


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    # set our local database:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/volta'
    # to stop loggin messages when we do anything:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # to know the state of the db when we run a function (it shows the sql queries that are happening behind scenes):
    SQLALCHEMY_ECHO = True

    # session configs: (a session is used to store information related to a user, across different requests, as they interact with a web app)
    SESSION_TYPE = 'redis'  # specifies which type of session interface to use
    SESSION_PERMANENT = False  # indicates whether to use permanent sessions
    SESSION_USE_SIGNER = True  # indicates whether to sign the session cookie identifier
    SESSION_REDIS = redis.from_url('redis://127.0.0.1:6379')  # specifies the Redis instance

    # To run the react frontend part is mandatory uncomment this two configs, but is not to running it in postman which is just http
    # SESSION_COOKIE_SAMESITE = 'None'
    # SESSION_COOKIE_SECURE = True
