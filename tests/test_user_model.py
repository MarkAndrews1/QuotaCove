import os
from unittest import TestCase
from flask import g

from models import db, User

os.environ['DATABASE_URL'] = "postgresql:///quotacove-test"

from app import app

class UserModelTestCase(TestCase):
    """Tests the User model"""

    def create_app(self):
        """Creates the app"""

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

        return app
    
    
    def setUp(self):
        """Creates test client, and sample data"""

        self.client = app.test_client()

        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()


    def tearDown(self):
        """Tear down the test enviroment"""

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_model(self):
        """Test to see if basic model works"""

        test_user = User(
                     username="test",
                     email="test@test.com",
                     password="HASHED_PASSWORD"
                     )
        
        db.session.add(test_user)
        db.session.commit()

        self.assertEqual(len(test_user.quotes), 0)
        self.assertEqual(len(test_user.followers), 0)
        self.assertEqual(len(test_user.following), 0)

        self.assertEqual(test_user.username, 'test')
        self.assertEqual(test_user.email, 'test@test.com')
        self.assertEqual(test_user.img_url, '/static/images/default.jpg')


    def test_delete_user(self):
        """Test deleting a user"""

        user = User(
            username='delete_me',
            email='test@test.com',
            password='delete'
        )

        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(User.query.filter_by(username='delete_me').first())

        db.session.delete(user)
        db.session.commit()

        self.assertIsNone(User.query.filter_by(username='delete_me').first())

    def test_user_login(self):
        """Tests logging in"""

        test_user = User(
                     username="test",
                     email="test@test.com",
                     password="HASHED_PASSWORD"
                     )
        
        db.session.add(test_user)
        db.session.commit()

        res = self.client.post('/login', data={'username':'test', 'password':'HASHED_PASSWORD'})
        self.assertEqual(res.status_code, 200)


    def test_user_logout(self):
        """Tests logging out"""

        test_user = User(
                     username="test",
                     email="test@test.com",
                     password="HASHED_PASSWORD"
                     )
        
        db.session.add(test_user)
        db.session.commit()

        with self.client:
            self.client.post('/login', data={'username':'test', 'password':'HASHED_PASSWORD'}, follow_redirects=True)

            res = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(res.status_code, 200)

    def test_user_following(self):
        """Test the following and follower relationships"""

        user1 = User(
            username='user1',
            email='user1@gmail.com',
            password='password1'
            )

        user2 = User(
            username='user2',
            email='user2@gmail.com',
            password='password2'
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user1.following.append(user2)
        db.session.commit()

        self.assertEqual(len(user1.following), 1)
        self.assertEqual(len(user2.followers), 1)

        user1.following.remove(user2)
        db.session.commit()

        self.assertEqual(len(user1.following), 0)
        self.assertEqual(len(user2.followers), 0)