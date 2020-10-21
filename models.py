from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """ Model of a User of the app """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)

    boards = db.relationship('Board')

    def __repr__(self):
        return f"<User #{self.id}: Name: {self.first_name} {self.last_name}. Username: {self.username}>"

    @classmethod
    def signup(cls, first_name, last_name, username, password):
        """ Sign up a user. Hash password and add to db session."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """ Find user and password in database and authenticate"""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Board(db.Model):
    """ a collection of Posts """

    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    posts = db.relationship("Post")

class Post(db.Model):
    """ an item pinned to a board """

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    complete_by = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id', ondelete='cascade'))


def connect_db(app):
    """ Connect database to the Flask app """

    db.app = app
    db.init_app(app)

