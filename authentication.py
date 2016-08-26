# authentication.py

from functools import wraps

from flask_restful.reqparse import RequestParser
from flask import make_response, g

import jwt

from models import *
from utils import jsend


def generate_token(id, user_salt):
    return jwt.encode({'id': id, 'user_salt': user_salt}, 'VERY SECRET KEY', algorithm='HS256')


def verify_token(token):
    try:
        return jwt.decode(token, 'VERY SECRET KEY', algorithm='HS256')
    except:
        return None


def login_required(f):
    @jsend
    @wraps(f)
    @orm.db_session
    def wrapper(*args, **kwargs):
        parser = RequestParser()
        parser.add_argument('token', type=str, required=False)
        args = parser.parse_args()
        if args.get('token', None):
            token = args['token']
        else:
            return ('fail', {'message': 'Please enter the token'}, 403)

        info = verify_token(token)
        print('info4')
        if not info:
            return 'fail', {'message': 'Token is invalid'}, 403


        u = User.select(lambda p: p.id == info['id'])[:]
        g.user = u[0]

        return f(*args, **kwargs)
    return wrapper


# @auth.error_handler
# def auth_error():
#     return make_response('', 401)
#
#
# @orm.db_session
# def verify_token(token):
#     try:
#         id = Serializer('VERY SECRET KEY').loads(token)
#     except BadSignature:
#         return None
#
#     return User.select(lambda p: p.id == id)[:]
#
#
# @auth.verify_password
# @orm.db_session
# def verify_password(username, password):
#     u = verify_token(username)
#     if not u:
#         u = User.select(lambda p: p.username == username)[:]
#         if not u or not u[0].password == password:
#             return False
#     g.user = u[0]
#     return True
