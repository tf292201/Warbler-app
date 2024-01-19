import unittest
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import User, Message, Follows, Likes, db, connect_db

class WarblerModelTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test environment."""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

        self.client = app.test_client()
        self.app = app
        self.counter = 0

        with app.app_context():
            db.init_app(app)
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_model(self):
        with self.app.app_context():
            bcrypt_instance = Bcrypt()

            # Create a user
            user = User(
                email='test@example.com',
                username=f'testuser_{self.counter}',
                password=bcrypt_instance.generate_password_hash('password').decode('utf-8'),
                image_url='/static/images/test.jpg',
                header_image_url='/static/images/header.jpg',
                bio='Test bio',
                location='Test location'
            )
            db.session.add(user)
            db.session.commit()

            db.session.refresh(user)

            # Check if the user is added to the database
            self.assertEqual(User.query.count(), 1)

            # Check if the user is correctly represented
            self.assertEqual(repr(user), f"<User #{user.id}: {user.username}, {user.email}>")


            # Create a followed user
            followed_user = User(
                email='followed@example.com',
                username='followeduser',
                password='password',
                image_url='/static/images/followed.jpg',
                header_image_url='/static/images/header.jpg',
                bio='Followed bio',
                location='Followed location'
            )
            db.session.add(followed_user)
            db.session.commit()

            user.following.append(followed_user)
            db.session.commit()

            db.session.refresh(user)

            # check the length of following list
            self.assertEqual(len(user.following), 1)

    def test_message_model(self):
        with self.app.app_context():
            bcrypt_instance = Bcrypt()

            # Create a user with a unique username
            username = f'testuser_{self.counter}'
            self.counter += 1
            user = User(
                email='test@example.com',
                username=username,
                password=bcrypt_instance.generate_password_hash('password').decode('utf-8'),
                image_url='/static/images/test.jpg',
                header_image_url='/static/images/header.jpg',
                bio='Test bio',
                location='Test location'
            )
            db.session.add(user)
            db.session.commit()

            db.session.refresh(user)

            # Create a message
            message_text = 'Test message'
            message = Message(
                text=message_text,
                timestamp=datetime.utcnow(),
                user_id=user.id
            )
            db.session.add(message)
            db.session.commit()

            db.session.refresh(user)

            # Check if the message is added to the database
            self.assertEqual(Message.query.count(), 1)

            # Check if the message is correctly represented
            self.assertEqual(repr(message), f"<Message {message.id}>")

            # Check if the message can be liked by a user
            liker = User(
                email='liker@example.com',
                username='likeruser',
                password='password',
                image_url='/static/images/liker.jpg',
                header_image_url='/static/images/header.jpg',
                bio='Liker bio',
                location='Liker location'
            )
            db.session.add(liker)
            db.session.commit()

            message.likes.append(Likes(user_id=liker.id))
            db.session.commit()

            self.assertEqual(len(message.likes), 1)
            self.assertEqual(len(liker.likes), 1)

if __name__ == '__main__':
    unittest.main()
