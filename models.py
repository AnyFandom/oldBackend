from pony import orm

db = orm.Database()

class User(db.Entity):
    login = orm.Required(str)
    password = orm.Required(str)
    description = orm.Optional(str)
    avatar = orm.Optional(str,default='https://static.lunavod.ru/img/users/1/avatar_100x100.png')
    keys = orm.Set('UserKey')


class UserKey(db.Entity):
    key = orm.Required(str)
    user = orm.Required(User)