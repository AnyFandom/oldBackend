# models.py

from pony import orm

db = orm.Database()


class User(db.Entity):
    username = orm.Required(str)
    password = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    user_salt = orm.Required(str)
    # keys = orm.Set('UserToken')
    posts = orm.Set('Post')

# class UserToken(db.Entity):
#     token = orm.Required(str)
#     user = orm.Required(User)

class Post(db.Entity):
    title = orm.Required(str)
    content = orm.Required(str)
    owner = orm.Required(User)
