"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup('test1', 'email1@email.com', 'password', None)
        userid1 = 1111
        user1.id = userid1

        user2 = User.signup('test2', 'email2@email.com', 'password', None)
        userid2 = 2222
        user2.id = userid2

        db.session.commit()

        user1 = User.query.get(userid1)
        user2 = User.query.get(userid2)

        self.user1 = user1
        self.userid1 = userid1

        self.user2 = user2
        self.userid2 = userid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        # Tests for following #

    def test_user_follow(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user1.followers), 0)

        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)

    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    # signup tests #

    def test_valid_signup(self):
        u_test = User.signup(
            'testthisisatest', 'testing@stest.com', 'password', None)
        userid = 99999
        u_test.id = userid
        db.session.commit()

        u_test = User.query.get(userid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, 'testthisisatest')
        self.assertEqual(u_test.email, 'testing@stest.com')
        self.assertNotEqual(u_test.password, 'password')
        self.assertTrue(u_test.password.startswith('$2b$'))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)

        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    #Tests for authentication#

    def test_valid_authentication(self):
        u = User.authenticate(self.user1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.userid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "badpassword"))
