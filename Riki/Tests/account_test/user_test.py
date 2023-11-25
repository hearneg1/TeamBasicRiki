import os
import sys
import unittest
from flask import Flask, url_for, redirect
from wiki import create_app
from wiki.web.user import UserManager
from wiki.web.user import UserRegistrationController
from wiki.web.forms import RegisterForm


# run with python -m unittest Tests/file_storage_test.py
def mock_flash(message, category):
    pass


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
            'name': 'test',
            'password': 'test_password'
        }
        login_response = self.client.post('/user/login/', data=form_data, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Login successful", login_response.data.decode('utf-8'))

    def test_user_login_success(self):
        form_data = {
            'name': 'tt',
            'password': 'test_password'
        }
        login_response = self.client.post('/user/login/', data=form_data, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Errors occured verifying your input. Please check the marked fields below.",
                      login_response.data.decode('utf-8'))

    def test_account_page_display_properly(self):
        form_data = {
            'name': 'name',
            'password': '1234'
        }
        login_response = self.client.post('/user/login/', data=form_data, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Login successful", login_response.data.decode('utf-8'))

        response = self.client.get('/user/', follow_redirects=True)
        decoded_response = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn("'s Profile", decoded_response, "user name is not properly displaying")
        self.assertIn("Active:", decoded_response, "Active is not properly displaying")
        self.assertIn("Authenticated:", decoded_response, "Authenticated is not properly displaying")
        self.assertIn("Roles:", decoded_response, "Roles is not properly displaying")
        self.assertIn("Delete Profile", decoded_response, "Delete Profile button is not displaying")
        # print(login_response.data)

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
        # Check if the user exists
        test_user_before = self.user_manager.get_user('new_user')

        # If the user doesn't exist, create it
        if not test_user_before:
            with self.app.test_request_context():
                form_data = {
                    'username': 'new_user',
                    'password': 'new_password',
                    'confirmPassword': 'new_password',
                    'email': 'new_user@example.com'
                }
                form = RegisterForm(data=form_data)

                # Use the register_user method to register the user
                with self.app.test_request_context():
                    result = self.registration_controller.register_user(form)

        # Now, proceed with the deletion part
        self.assertIsNotNone(test_user_before, "User does not exist")
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
