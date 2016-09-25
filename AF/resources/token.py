from flask import g
from flask_restful import Resource

from pony import orm

from AF.utils import Error, jsend, parser
from AF.models import User


class Token(Resource):
    @jsend
    @orm.db_session
    def post(self):
        args = parser(g.args,
            ('username', str, True),
            ('password', str, True))
        if not args:
            raise Error('E1101')

        user = User.get(username=args['username'])
        if not user or not user.check_password(args['password']):
            raise Error('E1002')

        token = user.generate_auth_token()

        return 'success', {'token': str(token, 'utf8')}, 201
