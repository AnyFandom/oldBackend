import jwt
import hashlib

from datetime import datetime
from pony import orm
import random
import string

from AF import app, db


class User(db.Entity):
    username = orm.Required(str, unique=True)
    password_hash = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='/static/img/default_avatar.jpg')
    user_salt = orm.Optional(str, default=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32)))
    created_at = orm.Optional(datetime, default=datetime.utcnow())

    posts = orm.Set('Post')
    comments = orm.Set('Comment')
    blogs = orm.Set('Blog')
    lastComments = orm.Set('LastComment')

    def hash_password(password):
        return hashlib.sha256(str(password).encode()).hexdigest()

    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

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
    preview_image = orm.Optional(str, default='/static/img/default_preview.jpg')
    owner = orm.Required(User)
    comments = orm.Set('Comment')
    created_at = orm.Optional(datetime, default=datetime.utcnow())
    blog = orm.Required('Blog')
    lastComments = orm.Set('LastComment')


class Comment(db.Entity):
    content = orm.Required(str)
    answers = orm.Set('Comment', reverse='parent')
    parent = orm.Optional('Comment', reverse='answers')
    depth = orm.Required(int)
    post = orm.Required(Post)
    owner = orm.Required(User)
    created_at = orm.Optional(datetime, default=datetime.utcnow())


class Fandom(db.Entity):
    title = orm.Required(str, unique=True)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='/static/img/default_avatar.jpg')
    created_at = orm.Optional(datetime, default=datetime.utcnow())
    blogs = orm.Set('Blog')


class Blog(db.Entity):
    title = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='/static/img/default_avatar.jpg')
    created_at = orm.Optional(datetime, default=datetime.utcnow())
    fandom = orm.Required(Fandom)
    posts = orm.Set(Post)
    owner = orm.Required(User)


class LastComment(db.Entity):
    user = orm.Required('User')
    post = orm.Required('Post')
    last_id = orm.Required(int)
