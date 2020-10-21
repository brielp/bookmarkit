import os
from unittest import TestCase

from models import db, connect_db, Post, Board, User


os.environ['DATABASE_URL'] = "postgresql://postgres:password@localhost:5433/bookmarkit-test"

from app import app


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class BoardViewTestCase(TestCase):
    """ Test views for posts """

    def setUp(self):
        """ Create test client and add sample data """

        User.query.delete()
        Post.query.delete()
        Board.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(first_name="Johnny", last_name="lingo", username="testuser", password="password")
        self.testuser_id = 20
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_add_board(self):
        """ Can user add a board ? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess["curr_user"] = self.testuser_id
            
            resp = c.post("/boards/add", data={"title": "TestBoard", "description": "testing the board"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("TestBoard", str(resp.data))

    def test_add_board_no_session(self):
        with self.client as c:
            resp = c.post("/boards/add", data={"title": "TestBoard", "description": "testing the board"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_board_delete(self):

        b = Board(id=1234, title="test", description="test", user_id=self.testuser_id)

        db.session.add(b)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["curr_user"] = self.testuser_id

            resp = c.get("/boards/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            b = Board.query.get(1234)
            self.assertIsNone(b)

    def test_unauthorized_board_delete(self):
        u = User.signup(first_name="John", last_name="Deere", username="jdeere", password="password")
        u.id = 124

        b = Board(id=1234, title="test", description="test", user_id=self.testuser_id)
        db.session.add_all([u, b])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["curr_user"] = 124

            resp = c.get("/boards/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

class PostViewTestCase(TestCase):

    def setUp(self):
        """ Create test client and add sample data """

        User.query.delete()
        Post.query.delete()
        Board.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(first_name="Johnny", last_name="lingo", username="testuser", password="password")
        self.testuser_id = 20
        self.testuser.id = self.testuser_id

        db.session.commit()

        b = Board(id=3, title="test", description="test", user_id=self.testuser_id)

        db.session.add(b)
        db.session.commit()

        b = Board.query.get(3)

        self.board = b
        self.board_id = 3

    def test_add_post(self):
        """ Can user add a post? """

        with self.client as c:
            with c.session_transaction() as sess:
                sess["curr_user"] = self.testuser_id
            
            resp = c.post("/boards/3/posts/add", data={"url": "https://www.google.com/", "complete_by": None}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Google", str(resp.data))

    def test_add_post_no_session(self):
        with self.client as c:
            resp = c.post("/boards/3/posts/add", data={"url": "https://www.google.com/", "complete_by": None}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_post_delete(self):

        p = Post(id=1234, title="test", description="test", url="https://www.google.com/", image_url="https://www.google.com/", board_id=self.board_id)

        db.session.add(p)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["curr_user"] = self.testuser_id

            resp = c.get("/boards/3/posts/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            p = Post.query.get(1234)
            self.assertIsNone(p)

    def test_unauthorized_board_delete(self):
        u = User.signup(first_name="John", last_name="Deere", username="jdeere", password="password")
        u.id = 124

        p = Post(id=1234, title="test", description="test", url="https://www.google.com/", image_url="https://www.google.com/", board_id=self.board_id)
        db.session.add_all([u, p])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess["curr_user"] = 124

            resp = c.get("/boards/3/posts/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))






        