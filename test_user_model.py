""" User model tests. """


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Board, Post

os.environ['DATABASE_URL'] = "postgresql://postgres:password@localhost:5433/bookmarkit-test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):

        User.query.delete()
        Board.query.delete()
        Post.query.delete()

        u1 = User.signup("Test", "User", "testuser1", "password")
        u1id = 10
        u1.id = u1id

        db.session.commit()

        self.u1 = User.query.get(u1id)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """ Basic working model - create """
        u = User(
            first_name = "Billy",
            last_name = "John",
            username = "bjohn",
            password = "password",
            id = 2020
        )

        db.session.add(u)
        db.session.commit()

        savedUser = User.query.get(2020)

        self.assertEqual(savedUser.username, u.username)
    
    def test_valid_signup(self):
        u_test = User.signup("tester", "tester", "tester123", "password")
        uid = 12
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)

        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "tester123")
        self.assertNotEqual(u_test.password, "password")
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup("Shory", "Putty", None, "password")
        uid = 383838
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("Mr.", "Morton", "username", None)

    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1.id)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_invalid_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))