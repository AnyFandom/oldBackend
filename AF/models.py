import jwt

from datetime import datetime
from pony import orm
import random
import string

from AF import app, db


class User(db.Entity):
    username = orm.Required(str, unique=True)
    password = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    user_salt = orm.Optional(str, default=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32)))
    registration_date = orm.Optional(datetime, default=datetime.utcnow())

    posts = orm.Set('Post')
    comments = orm.Set('Comment')
    blogs = orm.Set('Blog')

    def check_password(self, password):
        return self.password == password

    def generate_auth_token(self):
        return jwt.encode({'id': self.id, 'user_salt': self.user_salt}, app.config['SECRET_TOKEN_KEY'], algorithm='HS256')

    def check_auth_token(token):
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_TOKEN_KEY'], algorithm='HS256')
            user = User[decoded_token['id']]
            if user.user_salt != decoded_token['user_salt']:
                return None

            return user
        except (jwt.exceptions.InvalidTokenError, orm.core.ObjectNotFound):
            return None


class Post(db.Entity):
    @property
    def comment_count(self):
        return len(self.comments)

    title = orm.Required(str)
    content = orm.Required(str)
    preview_image = orm.Optional(str, default='https://www.betaseries.com/images/fonds/original/3086_1410380644.jpg')
    owner = orm.Required(User)
    comments = orm.Set('Comment')
    date = orm.Optional(datetime, default=datetime.utcnow())
    blog = orm.Required('Blog')


class Comment(db.Entity):
    content = orm.Required(str)
    answers = orm.Set('Comment', reverse='parent')
    parent = orm.Optional('Comment', reverse='answers')
    depth = orm.Required(int)
    post = orm.Required(Post)
    owner = orm.Required(User)
    date = orm.Optional(datetime, default=datetime.utcnow())


class Fandom(db.Entity):
    title = orm.Required(str, unique=True)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    date = orm.Optional(datetime, default=datetime.utcnow())
    blogs = orm.Set('Blog')


class Blog(db.Entity):
    title = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    date = orm.Optional(datetime, default=datetime.utcnow())
    fandom = orm.Required(Fandom)
    posts = orm.Set(Post)
    owner = orm.Required(User)
