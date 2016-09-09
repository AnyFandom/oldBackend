from datetime import datetime
from pony import orm
import random
import string

from AF import db


class User(db.Entity):
    id = orm.PrimaryKey(int, auto=True)

    username = orm.Required(str)
    password = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default="https://static.lunavod.ru/img/users/1/avatar_100x100.png")
    user_salt = orm.Optional(str, default=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32)))
    registration_date = orm.Optional(datetime, default=datetime.utcnow())

    rights = orm.Set('Staff')
    blogs = orm.Set('Blog')
    posts = orm.Set('Post')
    comments = orm.Set('Comment')


class Post(db.Entity):
    @property
    def comment_count(self):
        return len(self.comments)

    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    content = orm.Required(str)
    owner = orm.Required(User)
    comments = orm.Set('Comment')
    date = orm.Optional(datetime, default=datetime.utcnow())
    blog = orm.Required('Blog')


class Comment(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    content = orm.Required(str)
    answers = orm.Set('Comment', reverse='parent')
    parent = orm.Optional('Comment', reverse='answers')
    depth = orm.Required(int)
    post = orm.Required(Post)
    owner = orm.Required(User)
    date = orm.Optional(datetime, default=datetime.utcnow())


class Fandom(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default="https://static.lunavod.ru/img/users/1/avatar_100x100.png")
    date = orm.Optional(datetime, default=datetime.utcnow())
    blogs = orm.Set('Blog')
    staff = orm.Set('Staff')


class Blog(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default="https://static.lunavod.ru/img/users/1/avatar_100x100.png")
    date = orm.Optional(datetime, default=datetime.utcnow())
    fandom = orm.Required(Fandom)
    posts = orm.Set(Post)
    owner = orm.Required(User)
    staff = orm.Set('Staff')


class Staff(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    user = orm.Required(User)
    type = orm.Required(int)  # 1 - Global, 2 - Fandom, 3 - Blog
    role = orm.Required(int)  # 1 - Admin, 2 - Moder
    fandom = orm.Optional(Fandom)
    blog = orm.Optional(Blog)
