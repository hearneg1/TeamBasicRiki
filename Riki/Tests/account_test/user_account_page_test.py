import os
import sys
import unittest

from wiki import create_app
from wiki.web.user import UserManager
from wiki.web.user import UserRegistrationController
from wiki.web.forms import RegisterForm

# to test run python -m unittest .\Tests\account_test\user_account_page_test.py in command line

class UserAccountPageTestCases(unittest.TestCase):
    def setUp(self):
        directory = os.getcwd()
        self.app = create_app(directory=directory)
        self.client = self.app.test_client()
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.user_manager = UserManager(os.path.join(directory, 'user'))
        self.registration_controller = UserRegistrationController(self.user_manager)

    def test_account_page_display_success(self):
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
