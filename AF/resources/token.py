from flask import g
from flask_restful import Resource

from pony import orm

from AF.utils import error, generate_token, jsend, get_first, parser
from AF.models import User


class Token(Resource):
    @jsend
    @orm.db_session
    def post(self):
        args = parser(g.args,
            ('username', str, True),
            ('password', str, True))
        if not args:
            return error('E1101')

        user = get_first(list(User.select(lambda p: p.username == args['username'])[:]))
        if not user or not user.password == args['password']:
            return error('E1002')

        token = generate_token(user.id, user.user_salt)
        if not token:
            return 'error', 'Failed to generate token', 500

        return 'success', {'token': str(token, 'utf8')}, 201
