import os

import unittest

from flask import Blueprint
from wiki import create_app
from wiki.web.user import UserManager
from wiki.web.user import UserRegistrationController
from wiki.web.forms import RegisterForm

bp = Blueprint('wiki', __name__)

# to test run python -m unittest .\Tests\account_test\user_deletion_test.py in command line

class UserDeletionTestCases(unittest.TestCase):
    def _register_new_user(self, username):
        with self.app.test_request_context():
            form_data = {
                'username': username,
                'password': 'new_password',
                'confirmPassword': 'new_password',
                'email': 'new_user@example.com'
            }
            form = RegisterForm(data=form_data)

            # Use the register_user method to register the user
            with self.app.test_request_context():
                result = self.registration_controller.form_field_validation(form)

    def setUp(self):
        directory = os.getcwd()
        self.app = create_app(directory=directory)
        self.client = self.app.test_client()
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.user_manager = UserManager(os.path.join(directory, 'user'))
        self.registration_controller = UserRegistrationController(self.user_manager)

    def test_account_deletion_page_display(self):
        form_data = {
            'name': 'name',
            'password': '1234'
        }

        # Log in with the test user
        self.client.post('/user/login/', data=form_data, follow_redirects=True)
        self.client.get('/user', follow_redirects=True)
        response = self.client.get('/user/delete/name/', follow_redirects=True)
        decoded_response = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn(">Are you sure you want to delete the user", decoded_response, "User warning not displaying")
        self.assertIn('<button type="submit" class="btn btn-danger">Delete</button>', decoded_response,
                      'Delete button not displaying')

        # Check if the Cancel link is present
        self.assertIn('<a href="/user/" class="btn btn-secondary mt-2">Cancel</a>', decoded_response,
                      'Cancel link not displaying')

    def test_account_deletion(self):
        username = 'new_user'

        test_user_before = self.user_manager.get_user(username)

        # If the user doesn't exist, create it
        if not test_user_before:
            self._register_new_user(username)
            self.assertIsNotNone(self.user_manager.get_user(username), "User does not exist")

        form_data = {
            'name': 'new_user',
            'password': 'new_password'
        }

        # Log in with the test user
        self.client.post('/user/login/', data=form_data, follow_redirects=True)

        # Delete the test user
        response = self.client.post('/user/delete/new_user/', follow_redirects=True)
        decoded_response = response.data.decode('utf-8')

        # Check if the user no longer exists
        test_user_after = self.user_manager.get_user('new_user')

        # Perform assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("User new_user has been deleted.", decoded_response, "User not deleted")
        self.assertIn("Login", decoded_response, "Login page not redirected")
        self.assertIsNone(test_user_after, "User still exists after deletion")

    def test_account_deletion_cancel_button(self):
        form_data = {
            'name': 'name',
            'password': '1234'
        }

        # Log in with the test user
        self.client.post('/user/login/', data=form_data, follow_redirects=True)
        self.client.get('/user/', follow_redirects=True)
        response = self.client.get('/user/delete/name/', follow_redirects=True)
        decoded_response = response.data.decode('utf-8')

        # assure we hit the deletion page
        self.assertEqual(response.status_code, 200)
        self.assertIn(">Are you sure you want to delete the user", decoded_response, "User warning not displaying")

        # mimick cancel should return to user accout page
        cancel_response = self.client.get('/user/', follow_redirects=True)
        decoded_cancel_response = cancel_response.data.decode('utf-8')

        self.assertEqual(cancel_response.status_code, 200)
        self.assertIn("'s Profile", decoded_cancel_response
                      , "user name is not properly displaying")
        self.assertIn("Active:", decoded_cancel_response
                      , "Active is not properly displaying")
