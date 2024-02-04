import os
from unittest import TestCase
from models import db, User, Quote, Save, Tag
from app import app

os.environ['DATABASE_URL'] = "postgresql:///quotacove-test"

class QuoteModelTestCase(TestCase):
    """Tests the Quote Model"""

    def create_app(self):
        """Creates the app."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            self.uid = 94566
            u = User.signup("testing", "testing@test.com", "password", None)
            u.id = self.uid
            db.session.commit()

            self.u = User.query.get(self.uid)
            self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            res = super().tearDown()
            db.session.rollback()
            return res

    def test_quote_model(self):
        """Tests the basic model"""

        with app.app_context():
            q = Quote(
                text='test',
                author='user',
                user_id=self.uid
            )

            db.session.add(q)
            db.session.commit()

            self.u = User.query.get(self.uid)

            self.assertEqual(len(self.u.quotes), 1)
            self.assertEqual(self.u.quotes[0].text, 'test')

    def test_quote_delete(self):
        """Test the deletion of a quote"""

        with app.app_context():
            q = Quote(
                text='test',
                author='user',
                user_id=self.uid
            )

            db.session.add(q)
            db.session.commit()

            self.assertIsNotNone(Quote.query.get(q.id))

            with app.test_request_context():
                res = self.client.post(f'/quotes/delete/{q.id}', follow_redirects=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIsNone(Quote.query.get(q.id))


    def test_saving_quote(self):
        """Tests the saving and unsaving of a quote"""

        with app.app_context():
            q = Quote(
                text='test',
                author='user',
                user_id=self.uid
            )

            db.session.add(q)
            db.session.commit()

            u = User.signup("yetanothertest", "t@email.com", "password", None)
            uid = 888
            u.id = uid
            db.session.add(u)
            db.session.commit()

            u.saves.append(q)
            db.session.commit()

            saved_quote = Save.query.filter(Save.user_id == u.id).all()

            self.assertEqual(len(saved_quote), 1)
            self.assertEqual(saved_quote[0].quote_id, q.id)

            u.saves.remove(q)
            db.session.commit()

            unsaved_quote = Save.query.filter(Save.user_id == u.id).all()
            self.assertEqual(len(unsaved_quote), 0)

    def test_quote_tags(self):
        """Tests the tags of a quote"""

        with app.app_context():

            q = Quote(
                text='test',
                author='user',
                user_id=self.uid
            )

            db.session.add(q)
            db.session.commit()

            tag1 = Tag(name='tag1')
            tag2 = Tag(name='tag2')
            db.session.add_all([tag1, tag2])
            db.session.commit()

            q.tags.extend([tag1, tag2])
            db.session.commit()

            saved_quote = Quote.query.get(q.id)

            self.assertEqual(len(saved_quote.tags), 2)
            self.assertIn(tag1, saved_quote.tags)
            self.assertIn(tag2, saved_quote.tags)