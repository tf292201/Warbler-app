import os
import unittest
from unittest import TestCase

from models import db, Message, User
from app import app, CURR_USER_KEY

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

        # Create a test client
        self.client = app.test_client()

        # Set up the application context
        with app.app_context():
            # Create tables
            db.create_all()

            # Check if the user already exists
            self.testuser = User.query.filter_by(email="test@test.com").first()

            if not self.testuser:
                # Add sample data
                self.testuser = User.signup(username="testuser",
                                            email="test@test.com",
                                            password="testuser",
                                            image_url=None)

                db.session.commit()

                # Refresh the user instance to avoid DetachedInstanceError
                self.testuser = User.query.get(self.testuser.id)

    def tearDown(self):
        """Clean up resources after each test."""
        with app.app_context():
            db.session.rollback()
            db.drop_all()

    def test_add_message(self):
        """Can use add a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            
            resp = c.post("/messages/new", data={"text": "Hello"})

            # print(resp.get_data(as_text=True))
        
            self.assertEqual(resp.status_code, 200)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    # Other test methods...

if __name__ == '__main__':
    unittest.main()
