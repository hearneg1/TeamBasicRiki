"""
This integration tests file houses the automated integration tests for the three new features

Upload/Download Feature:
This feature is tested through route calls and using a file storage object. Due to the nature of the download process,
it had to be tested manually. See the manual integration test folder and acceptance tests.

User Registration Feature:
This feature was tested through both routes and objects.

Wiki Download Feature:
This feature could not be tested through routes but was thoroughly tested through acceptance tests.
This file has mocked objects to test the rest of the feature.


"""


import os
import sys
import unittest
from unittest.mock import Mock
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)
from werkzeug.datastructures import FileStorage
from wiki.web.file_storage import FileManager
from wiki.web.user import UserManager
from wiki.web.user import UserRegistrationController
from wiki.web.forms import RegisterForm
from wiki.web.converter import Converter, get_file_size
from wiki import create_app


class test_file_upload_download_delete(unittest.TestCase):

    def setUp(self):
        directory = os.getcwd()
        self.app = create_app(directory=directory)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.directory = os.path.join("Tests", "test_directory")
        self.file_manager = FileManager(self.directory)

    def test_Upload_routes(self):
        file = FileStorage(  # Used to copy how flask's upload file structure creates a file
            filename="test_file.docx",
            content_type="text/plain"
        )
        # login data for the system
        test_login_data = {
            'name': 'name',
            'password': '1234'
        }

        # logs in to the system
        login_response = self.client.post('/user/login/', data=test_login_data, follow_redirects=True)
        decoded_response = login_response.data.decode('utf-8')
        self.assertIn("Login successful", decoded_response)
        self.assertEqual(login_response.status_code, 200)

        # after logging in, moves to file storage page
        self.client.post('/file_storage/')

        # begins testing uploading of a file
        with open('Tests/integration_tests_files/test.pdf', 'rb') as file:
            data = {'file': (file, 'test.pdf')}
            response = self.client.post('/upload_file/', data=data, follow_redirects=True)
        decoded_response = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully uploaded", decoded_response)

    def test_upload_delete(self):

        test_file = FileStorage(  # Used to copy how flask's upload file structure creates a file
            filename="test.docx",
            content_type="text/plain"
        )

        #tests uploading the test file and asserts it is in the files
        upload_status = self.file_manager.upload_file(test_file)
        self.assertTrue(upload_status)
        self.assertIn(test_file.filename, self.file_manager.get_downloadable_files())

        #tests deleting the test file and asserts it is not in the files
        delete_status = self.file_manager.delete_file(test_file.filename)
        self.assertTrue(delete_status)
        self.assertNotIn(test_file.filename, self.file_manager.get_downloadable_files())

    def tearDown(self):
        if os.path.exists('UserFileStorage/test.pdf'):
            os.remove('UserFileStorage/test.pdf')

        if os.path.exists('Tests/test_directory/test.docx'):
            os.remove('Tests/test_directory/test.docx')

        if os.path.exists('Tests/test_directory/testing_upload.docx'):
            os.remove('Tests/test_directory/testing_upload.docx')


class User_Registration_Testing(unittest.TestCase):
    def setUp(self):
        directory = os.getcwd()
        self.app = create_app(directory=directory)
        self.client = self.app.test_client()
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.user_manager = UserManager(os.path.join(directory, 'user'))
        self.registration_controller = UserRegistrationController(self.user_manager)

    def test_create_delete_account_routes(self):
        # creates test data for logging in and new account
        testing = {
            'username': 'test_user3',
            'password': 'test_password',
            'confirmPassword': 'test_password',
            'email': 'test_user@example.com'
        }

        test_login_data = {
            'name': 'test_user3',
            'password': 'test_password'
        }

        # creates new account and verifies it was added through the route
        response = self.client.post('/user/create/', data=testing, follow_redirects=True)
        decoded_response = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn("User added successfully!", decoded_response)

        # attempts login with test login and ensures successful login
        login_response = self.client.post('/user/login/', data=test_login_data, follow_redirects=True)
        decoded_response = login_response.data.decode('utf-8')
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Login successful", decoded_response)

        # navigates to profile page
        self.client.post('/user/')

        # deletes and asserts the user has been deleted
        delete_response = self.client.post('/user/delete/test_user3/', follow_redirects=True)
        decoded_response = delete_response.data.decode('utf-8')
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("has been deleted", decoded_response)

    def test_create_delete_mocks(self):
        with self.app.test_request_context():
            test_account_data = RegisterForm(
                username='test_user3',
                password='test_password',
                confirmPassword='test_password',
                email='test_user@example.com'
            )
            # tests creating user by calling function directly
            self.registration_controller.form_field_validation(test_account_data)
            test_account_created = self.user_manager.get_user('test_user3')
            self.assertIsNotNone(test_account_created)

            # tests deleting user by invoking delete directly
            self.user_manager.delete_user('test_user3')
            test_account_deleted = self.user_manager.get_user('test_user3')
            self.assertIsNone(test_account_deleted)


class test_wiki_download(unittest.TestCase):
    def setUp(self):
        directory = os.getcwd()
        self.app = create_app(directory=directory)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.page = Mock()

    # Testing for wiki download feature that tests converting a file
    def test_convert(self):
        test_md_path = "Tests/integration_tests_files/test.md"  # gets the path of the test files that will be used
        test_pdf_path = "Tests/integration_tests_files/test.pdf"
        with open(test_md_path, 'r',
                  encoding='utf-8') as md_file:  # opens the test.md file and gets the page title and contents
            self.page.title = md_file.readline().strip()
            self.content = md_file.read()
        file_converter = Converter(self.page)  # creates converter object with the test.md file
        pdf_file_size = round(os.path.getsize(test_pdf_path) / 1024, 1)  # gets the size of the test.pdf file
        md_to_pdf, converted_size = file_converter.convert_to_PDF()
        md_to_pdf_size = float(
            converted_size.strip(" KB"))  # the size is returned as a string, so this converts the string to a float
        self.assertEqual(pdf_file_size, round(md_to_pdf_size, 1))


if __name__ == '__main__':
    unittest.main()
