from datetime import datetime
from pony import orm

from AF import db


class User(db.Entity):
    username = orm.Required(str)
    password = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    user_salt = orm.Required(str)
    posts = orm.Set('Post')
    comments = orm.Set('Comment')


class Post(db.Entity):
    title = orm.Required(str)
    content = orm.Required(str)
    owner = orm.Required(User)
    comments = orm.Set('Comment')
    date = orm.Required(datetime)


class Comment(db.Entity):
    parent_id = orm.Required(int)
    post = orm.Required(Post)
    owner = orm.Required(User)
    content = orm.Required(str)
    date = orm.Required(datetime)
