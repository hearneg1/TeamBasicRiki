import os
import sys
import unittest
from flask import Flask, url_for, redirect, Blueprint
from wiki import create_app
from wiki.web.user import UserManager
from wiki.web.user import UserRegistrationController
from wiki.web.forms import RegisterForm

bp = Blueprint('wiki', __name__)

### run with  python -m unittest .\Tests\account_test\user_controller_test.py ###

class UserRegistrationControllerTestCase(unittest.TestCase):
    def setUp(self):
        directory = os.getcwd()
        self.app = create_app(directory=directory)
        self.client = self.app.test_client()
        self.user_manager = UserManager(os.path.join(directory, 'user'))
        self.registration_controller = UserRegistrationController(self.user_manager)

    def test_register_user_success(self):
        deleted_user = self.user_manager.get_user('new_user')
        if deleted_user:
            self.user_manager.delete_user('new_user')
        # create  form with user data
        with self.app.test_request_context():
            form_data = {
                'username': 'new_user',
                'password': 'new_password',
                'confirmPassword': 'new_password',
                'email': 'new_user@example.com'
            }
            form = RegisterForm(data=form_data)

        # register_user method for regristation
        with self.app.test_request_context():
            result = self.registration_controller.form_field_validation(form)

        # Print the result for debugging
        # print("Result:", result)

        # Check if the result is True (success)
        # self.assertTrue(result, flash('User added successfully!', 'success'))

        # Check if the user exists in the UserManager after addition
        added_user = self.user_manager.get_user('new_user')

        # Print added_user for debugging
        # print("Added User:", added_user)

        self.assertIsNotNone(added_user, "User 'new_user' should exist after registration")
        self.assertEqual(added_user.get('email'), 'new_user@example.com')

    def test_register_user_failure_existing_user(self):
        initial_user = self.user_manager.get_user('new_user')
        if not initial_user:
            with self.app.test_request_context():
                form_data = {
                    'username': 'new_user',
                    'password': 'new_password',
                    'confirmPassword': 'new_password',
                    'email': 'new_user@example.com'
                }
                form = RegisterForm(data=form_data)

            # register_user method for regristation
            with self.app.test_request_context():
                result = self.registration_controller.form_field_validation(form)

        # Create an initial user with the same username
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
            result = self.registration_controller.form_field_validation(form)

            # Print the result for debugging
        # print("Result:", result)

        # Check if the result is False (failure)
        self.assertFalse(result, "User registration should fail due to existing username")

        # Check if the user exists in the UserManager after addition
        added_user = self.user_manager.get_user('new_user')

        # Print added_user for debugging
        # print("Added User:", added_user)

        self.assertIsNotNone(added_user, "Existing user should still exist")
        self.assertEqual(added_user.get('email'), 'new_user@example.com')

    def test_register_user_failure_password_mismatch(self):
        test_user = self.user_manager.get_user('new_user')
        if test_user:
            self.user_manager.delete_user('new_user')
        # Create a form with user data and mismatched passwords
        with self.app.test_request_context():
            form_data = {
                'username': 'new_user',
                'password': 'new_password',
                'confirmPassword': 'mismatched_password',
                'email': 'new_user@example.com'
            }
            form = RegisterForm(data=form_data)

        # Use the register_user method to attempt registration with mismatched passwords
        with self.app.test_request_context():
            result = self.registration_controller.form_field_validation(form)

        # Print the result for debugging
        # print("Result:", result)

        # Check if the result is False (failure)
        self.assertFalse(result, "User registration should fail due to password mismatch")

        # Check if the user does not exist in the UserManager
        non_existent_user = self.user_manager.get_user('new_user')

        # Print non_existent_user for debugging
        # print("Non-existent User:", non_existent_user)

        self.assertIsNone(non_existent_user, "User 'new_user' should not exist after failed registration")

    def test_user_delete(self):
        initial_user = self.user_manager.get_user('new_user')
        if not initial_user:
            with self.app.test_request_context():
                form_data = {
                    'username': 'new_user',
                    'password': 'new_password',
                    'confirmPassword': 'new_password',
                    'email': 'new_user@example.com'
                }
                form = RegisterForm(data=form_data)

            # register_user method for regristation
            with self.app.test_request_context():
                result = self.registration_controller.form_field_validation(form)
        self.assertIsNotNone(initial_user, "User 'test_user' should exist before deletion")

        # Delete the user
        self.user_manager.delete_user('test_user')

        # Check if the user is deleted
        deleted_user = self.user_manager.get_user('test_user')
        self.assertIsNone(deleted_user, "User 'test_user' should be deleted")


if __name__ == '__main__':
    unittest.main()
