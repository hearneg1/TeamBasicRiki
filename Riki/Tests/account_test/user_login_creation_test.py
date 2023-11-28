import os
import sys
import unittest
from flask import Flask, url_for, redirect, Blueprint
from wiki import create_app
from wiki.web.user import UserManager
from wiki.web.user import UserRegistrationController
from wiki.web.forms import RegisterForm

bp = Blueprint('wiki', __name__)

# to test run python -m unittest .\Tests\account_test\user_login_creation_test.py in command line

class UserCreateRouteTestCase(unittest.TestCase):

    def setUp(self):
        directory = os.getcwd()
        self.app = create_app(directory=directory)
        self.client = self.app.test_client()
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.user_manager = UserManager(os.path.join(directory, 'user'))
        self.registration_controller = UserRegistrationController(self.user_manager)

    def test_register_page_access(self):
        response = self.client.get('/user/create/?')
        decoded_response = response.data.decode('utf-8')

        self.assertIn("<h1>Create Your Account</h1>", decoded_response, "Create you account header not found in page")
        self.assertIn("username", decoded_response, "Username field not found in page")
        self.assertIn("password", decoded_response, "Password field not found in page")
        self.assertIn("confirmPassword", decoded_response, "Confirm Password field not found in page")
        self.assertIn("email", decoded_response, "Email field not found in page")
        self.assertEqual(response.status_code, 200)
        # print(response.data)

    def test_register_page_post(self):
        deleted_user = self.user_manager.get_user('new_user2')
        if deleted_user:
            self.user_manager.delete_user('new_user2')
        form_data = {
            'username': 'new_user2',
            'password': 'new_password',
            'confirmPassword': 'new_password',
            'email': 'new_user@example.com'
        }
        response = self.client.post('/user/create/', data=form_data, follow_redirects=True)
        decoded_response = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn("User added successfully!", decoded_response, "Sign up message flash did not pop up")
        self.assertIn("Login", decoded_response, "Login button not displaying")
        self.assertIsNotNone(deleted_user, "create user is not in json")
        # print(response.data)

    def test_register_page_existing_user(self):
        form_data = {
            'username': 'new_user2',
            'password': 'new_password',
            'confirmPassword': 'new_password',
            'email': 'new_user@example.com'
        }
        response = self.client.post('/user/create/', data=form_data, follow_redirects=True)
        decoded_response = response.data.decode('utf-8')
        self.assertIn("Username already exists. Please choose another username.", decoded_response,
                      "user name flash did not pop up")
        self.assertIn("Sign up", decoded_response, "Sign up is not displaying")
        # print(response.data)

    def test_register_page_different_password(self):
        form_data = {
            'username': 'new_user3',
            'password': 'new_password',
            'confirmPassword': 'new_password2',
            'email': 'new_user@example.com'
        }
        response = self.client.post('/user/create/', data=form_data, follow_redirects=True)
        decoded_response = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Passwords do not match. Please enter matching passwords.", decoded_response,
                      "Sign up message flash did not pop up")
        self.assertIn("Sign up", decoded_response, "Sign up is not displaying")
        # print(response.data)

    def test_user_login_success(self):
        form_data = {
            'name': 'name',
            'password': '1234'
        }
        login_response = self.client.post('/user/login/', data=form_data, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Login successful", login_response.data.decode('utf-8'))

    def test_user_login_failure(self):
        form_data = {
            'name': 'tt',
            'password': 'test_password'
        }
        login_response = self.client.post('/user/login/', data=form_data, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Errors occured verifying your input. Please check the marked fields below.",
                      login_response.data.decode('utf-8'))

    def test_account_logout(self):
        form_data = {
            'name': 'name',
            'password': '1234'
        }

        # Log in with the test user
        self.client.post('/user/login/', data=form_data, follow_redirects=True)
        response = self.client.get('/user/logout/', follow_redirects=True)
        decoded_response = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Logout successful.", decoded_response, "User did not logout successfully")
        self.assertIn("Login", decoded_response, "Login page not redirected")


if __name__ == '__main__':
    unittest.main()
