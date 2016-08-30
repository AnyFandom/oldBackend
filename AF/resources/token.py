from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from pony import orm

from AF.utils import error, generate_token, jsend, get_first
from AF.models import User


class Token(Resource):
    @jsend
    @orm.db_session
    def post(self):
        parser = RequestParser(bundle_errors=True)
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        user = get_first(list(User.select(lambda p: p.username == args['username'])[:]))
        if not user or not user.password == args['password']:
            return error('E1002')

        token = generate_token(user.id, user.user_salt)
        if not token:
            return 'error', 'Failed to generate token', 500

        return 'success', {'token': str(token, 'utf8')}, 201
