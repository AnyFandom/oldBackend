from datetime import datetime
from pony import orm
import random
import string

from AF import db


class User(db.Entity):
    username = orm.Required(str)
    password = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    user_salt = orm.Optional(str, default=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16)))
    registration_date = orm.Optional(datetime, default=datetime.utcnow())

    posts = orm.Set('Post')
    comments = orm.Set('Comment')
    blogs = orm.Set('Blog')

    super = orm.Optional('Super')
    admin_in_fandoms = orm.Set('Fandom', reverse='admins')
    moder_in_fandoms = orm.Set('Fandom', reverse='moders')
    admin_in_blogs = orm.Set('Blog', reverse='admins')
    moder_in_blogs = orm.Set('Blog', reverse='moders')


class Post(db.Entity):
    @property
    def comment_count(self):
        return len(self.comments)

    title = orm.Required(str)
    content = orm.Required(str)
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
    title = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    date = orm.Optional(datetime, default=datetime.utcnow())
    blogs = orm.Set('Blog')

    admins = orm.Set(User, reverse='admin_in_fandoms')
    moders = orm.Set(User, reverse='moder_in_fandoms')


class Blog(db.Entity):
    title = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    date = orm.Optional(datetime, default=datetime.utcnow())
    fandom = orm.Required(Fandom)
    posts = orm.Set(Post)
    owner = orm.Required(User)

    admins = orm.Set(User, reverse='admin_in_blogs')
    moders = orm.Set(User, reverse='moder_in_blogs')


class Super(db.Entity):
    user = orm.Required(User)
    role = orm.Required(bool)  # 0 - admin, 1 - user
