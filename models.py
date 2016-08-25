from pony import orm
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

db = orm.Database()


class User(db.Entity):
    username = orm.Required(str)
    password = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str, default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    user_salt = orm.Required(str)
    # keys = orm.Set('UserToken')

# class UserToken(db.Entity):
#     token = orm.Required(str)
#     user = orm.Required(User)
