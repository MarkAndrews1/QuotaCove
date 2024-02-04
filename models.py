'''SQLAlchemy models for QuotaCove'''

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)


class Follow(db.Model):
    """Connects a follower to a followed user."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key = True
        )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key = True
        )
    


class User(db.Model):
    """Creates a user in the system"""

    __tablename__ = 'users'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    fav_quote = db.Column(
        db.Text,
        nullable=True,

    )

    fav_quote_author = db.Column(
        db.Text,
        nullable=True,
    )

    img_url = db.Column(
        db.Text,
        default="/static/images/default.jpg"
    )

    quotes = db.relationship('Quote', cascade="all, delete-orphan")

    saves = db.relationship(
        'Quote',
        secondary="saves",
        single_parent=True,
        passive_deletes=True
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin="User.id == Follow.user_following_id",
        secondaryjoin="User.id == Follow.user_being_followed_id",
        overlaps="following",
        back_populates="followers"
    )

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin="User.id == Follow.user_being_followed_id",
        secondaryjoin="User.id == Follow.user_following_id",
        overlaps="followers",
        back_populates="following"
    )

    def __repr__(self):
        return f"User #{self.id}: {self.username}, {self.email}"
    
    @classmethod
    def signup(cls, username, email, password, fav_quote, fav_quote_author, img_url):
        """Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            fav_quote=fav_quote,
            fav_quote_author=fav_quote_author,
            img_url=img_url
        )

        db.session.add(user)

        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Try and find user with the username and password.
        If no match or wrong credentials return False.
        """
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False
    


class Quote(db.Model):
    """Creates a new quote and adds to system."""

    __tablename__ = 'quotes'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    text = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    author = db.Column(
        db.Text,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')
    saves = db.relationship('Save')


class Tag(db.Model):
    """Creates a new tag"""

    __tablename__ = "tags"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True) 
    
    name = db.Column(
        db.Text,
        unique=True
    )

    quotes = db.relationship('Quote', secondary='quote_tags', backref='tags')


class QuoteTag(db.Model):
    """Adds tag to quote"""

    __tablename__ = 'quote_tags'

    post_id = db.Column(
        db.Integer,
        db.ForeignKey('quotes.id'),
        primary_key=True
    )

    tag_id = db.Column(
        db.Integer,
        db.ForeignKey('tags.id', ondelete='cascade'),
        primary_key=True
    )


class Save(db.Model):
    """Mapping user saves to quotes"""

    __tablename__ = 'saves'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    quote_id = db.Column(
        db.Integer,
        db.ForeignKey('quotes.id', ondelete='cascade')
    )


