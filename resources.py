import random
import string

from flask_restful import Resource, marshal_with
from flask_restful.reqparse import RequestParser
from flask import make_response, url_for, g, request

import jwt

from models import *
from utils import *
from authentication import *


class Token(Resource):
    @jsend
    @orm.db_session
    def post(self):
        parser = RequestParser()
        parser.add_argument('username', type=str, required=False)
        parser.add_argument('password', type=str, required=False)
        args = parser.parse_args()

        if args.get('username', None) and args.get('password', None):
            auth = {'username': args['username'], 'password': args['password']}
        else:
            return 'fail', {'title': 'Please enter username and password'}, 403

        u = User.select(lambda p: p.username == auth['username'])[:]
        if not u or not u[0].password == auth['password']:
            return 'fail', {'title': 'Wrong username or password'}, 403

        token = generate_token(u[0].id, u[0].user_salt)
        if not token:
            return 'error', 403
        return 'success', {'token': str(token, 'utf8')}, 201


class UserItem(Resource):
    @orm.db_session
    @marshal_with(user_marshaller)
    def get(self, id):
        return User[id]


class UserList(Resource):
    @orm.db_session
    def post(self):
        parser = RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('avatar', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        args = parser.parse_args()

        salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        u = User(username=args.username, password=args.password, user_salt=salt)
        if args.get('avatar', None):
            u.avatar = args['avatar']
        if args.get('description', None):
            u.description = args['description']

        db.commit()

        resp = make_response('', 201)
        resp.headers['Location'] = url_for('useritem', id=u.id)
        return resp

    @orm.db_session
    @marshal_with(user_marshaller)
    def get(self):
        return list(User.select()[:])
