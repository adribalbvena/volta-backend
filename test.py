import unittest
from unittest.mock import patch
import requests
from main import app
from models import User


#
# patch explanation: When applied to a test method, the @patch decorator specifies which objects or functions should be
# patched with a mock implementation. It allows you to replace dependencies of the code under test with mock objects,
# enabling you to control their behavior and assert against expected interactions.
class VoltaTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client()
        # Create a new application context
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        # Pop the application context when the test is finished
        self.app_context.pop()

    @patch('main.User.query')  # Mock the User.query method, we need to call it from where is used, not defined
    @patch('main.db.session')  # Mock the db.session object
    @patch('main.create_uuid')  # Mock the create_uuid function
    def test_register_success(self, create_uuid_mock, session_mock, query_mock):
        create_uuid_mock.return_value = '60f89147f0284d62a983c1ab32a721c4'  # The response value will be this id
        query_mock.filter_by.return_value.first.return_value = None  # the real function is typically used to query
        # the database for a matching record. In this case, it is being used to mock the scenario where no existing
        # user is found with the specified email.
        session_mock.add.return_value = None  # this it is being used to mock the successful addition of the user
        # object to the session.
        # Make a POST request to the /register endpoint
        response = self.client.post('/register', json={'email': 'test@example.com', 'password': 'password'})
        # Assert the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert the response JSON matches the expected values
        self.assertEqual(response.json, {'email': 'test@example.com', 'id': '60f89147f0284d62a983c1ab32a721c4'})

    @patch('main.User.query')  # Mock the User.query method
    @patch('main.bcrypt.check_password_hash')  # Mock the bcrypt.check_password_hash method
    def test_login_success(self, bcrypt_mock, query_mock):
        # Mock the return value of the User.query method
        user_mock = User(id='user_id', email='test@example.com', password='password')
        query_mock.filter_by.return_value.first.return_value = user_mock
        # Set the return value of bcrypt.check_password_hash
        bcrypt_mock.return_value = True
        # Make a POST request to the /login endpoint
        response = self.client.post('/login', json={'email': 'test@example.com', 'password': 'password'})
        # Assert the response status code is 200 which is successful
        self.assertEqual(response.status_code, 200)
        # Assert the response JSON matches the expected values
        self.assertEqual(response.json, {'id': 'user_id', 'email': 'test@example.com'})

    def test_logout_success(self):
        # Set a user_id value in the session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'user_id'
        # Make a POST request to the /logout endpoint
        response = self.client.post('/logout')
        # Assert the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert the response JSON matches the expected message
        self.assertEqual(response.json, {'message': 'Logged out successfully'})
        # Assert that the user_id key is removed from the session
        with self.client.session_transaction() as sess:
            self.assertNotIn('user_id', sess)

    @patch('main.requests.get')  # This mock allows the test to intercept the call to requests.get and provide a
    # mocked response instead of making a real HTTP request.
    def test_get_plan_success(self, get_mock):
        # Set up mock response from the API
        mock_data = {'result': 'mock data'}
        mock_response = requests.Response()
        mock_response.status_code = 200  # here we are forcing the response status code of our mock response
        mock_response.json = lambda: mock_data
        get_mock.return_value = mock_response
        # Make a GET request to the /get_plan endpoint with query parameters
        response = self.client.get('/get_plan?days=3&destination=London')
        # Assert the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert the response JSON matches the expected data
        self.assertEqual(response.json, mock_data)


if __name__ == '__main__':
    unittest.main()
