"""
User Classes & Helpers
~~~~~~~~~~~~~~~~~~~~~~

This module defines classes and helpers for user management in a Flask application.

Classes:
- `UserManager`: A simple user manager that saves user data as JSON.
- `UserRegistrationController`: Handles user registration and form field validation.
- `User`: Represents a user with methods for retrieving and updating user data.

Helpers:
- `get_default_authentication_method`: Gets the default authentication method from the Flask app configuration.
- `make_salted_hash`: Generates a salted hash for a given password.
- `check_hashed_password`: Checks if a password matches a hashed password.
- `protect`: Decorator to protect routes based on the authentication status.

Usage:
    To use these classes and helpers, import them into your Flask application and
    instantiate the `UserManager` to manage user-related operations.

Example:
    user_manager = UserManager('/path/to/user_data')
    new_user = user_manager.add_user('username', 'password', email='user@example.com')
    if new_user:
        print(f"User {new_user.name} added successfully!")

Note:
    This is a basic implementation, and you may want to enhance it based on your application's requirements.
"""
import os
import json
import binascii
import hashlib
import uuid
from functools import wraps

from flask import current_app, flash
from flask_login import current_user


class UserManager(object):
    """A very simple user Manager, that saves it's data as json."""

    def __init__(self, path):
        self.file = os.path.join(path, 'users.json')

    def read(self):
        try:
            with open(self.file) as f:
                data = json.loads(f.read())
            return data
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading file: {e}")
            return {}

    def write(self, data):
        try:
            with open(self.file, 'w') as f:
                f.write(json.dumps(data, indent=2))
        except IOError as e:
            print(f"Error writing to file: {e}")

    def add_user(self, name, password, email, active=True, roles=[], authentication_method=None):
        users = self.read()
        if users.get(name):
            return False
        if authentication_method is None:
            authentication_method = get_default_authentication_method()
        new_user_id = str(uuid.uuid4())
        new_user = {
            'id': new_user_id,
            'active': active,
            'roles': roles,
            'authentication_method': authentication_method,
            'authenticated': False,
            'email': email,
            'is_anonymous': False
        }
        if authentication_method == 'hash':
            new_user['hash'] = make_salted_hash(password)
        elif authentication_method == 'cleartext':
            new_user['password'] = password
        else:
            raise NotImplementedError(authentication_method)
        users[name] = new_user
        print(f"Adding user: {new_user}")
        self.write(users)
        userdata = users.get(name)
        return User(self, name, userdata)

    def get_user(self, name):
        users = self.read()
        userdata = users.get(name)
        if not userdata:
            return None
        return User(self, name, userdata)

    def delete_user(self, name):
        users = self.read()
        if not users.pop(name, False):
            return False
        self.write(users)
        return True

    def update(self, name, userdata):
        data = self.read()
        data[name] = userdata
        self.write(data)




class UserRegistrationController:
    def __init__(self, user_manager):
        self.user_manager = user_manager

    def form_field_validation(self, form):
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirmPassword.data
        email = form.email.data

        #print(f"Attempting to register user: {username}")

        existing_user = self.user_manager.get_user(username)
        #print(existing_user)
        if existing_user is not None:
            #print(f"User {username} already exists. Registration failed.")
            flash('Username already exists. Please choose another username.', 'danger')
            return False

        if password != confirm_password:
            #print(f"Passwords do not match. Registration failed.")
            flash('Passwords do not match. Please enter matching passwords.', 'danger')
            return False

        user_added = self.user_manager.add_user(username, password, email=email)
        if user_added:
            #print(f"User {username} added successfully!")
            flash('User added successfully!', 'success')
            return True
        else:
            #print(f"Failed to add user {username}. Registration failed.")
            flash('Failed to add user. Please try again.', 'danger')
            return False



class User(object):
    def __init__(self, manager, name, data):
        self.manager = manager
        self.name = name
        self.data = data

    def get(self, option):
        return self.data.get(option)

    def set(self, option, value):
        self.data[option] = value
        self.save()

    def save(self):
        self.manager.update(self.name, self.data)

    def is_authenticated(self):
        return self.data.get('authenticated')

    def is_active(self):
        return self.data.get('active')

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.name

    def check_password(self, password):
        """Return True, return False, or raise NotImplementedError if the
        authentication_method is missing or unknown."""
        authentication_method = self.data.get('authentication_method', None)
        if authentication_method is None:
            authentication_method = get_default_authentication_method()
        # See comment in UserManager.add_user about authentication_method.
        if authentication_method == 'hash':
            result = check_hashed_password(password, self.get('hash'))
        elif authentication_method == 'cleartext':
            result = (self.get('password') == password)
        else:
            raise NotImplementedError(authentication_method)
        return result


def get_default_authentication_method():
    return current_app.config.get('DEFAULT_AUTHENTICATION_METHOD', 'cleartext')


def make_salted_hash(password, salt=None):
    if not salt:
        salt = os.urandom(64)
    d = hashlib.sha512()
    d.update(salt[:32])
    d.update(password)
    d.update(salt[32:])
    return binascii.hexlify(salt) + d.hexdigest()


def check_hashed_password(password, salted_hash):
    salt = binascii.unhexlify(salted_hash[:128])
    return make_salted_hash(password, salt) == salted_hash


def protect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_app.config.get('PRIVATE') and not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)

    return wrapper
