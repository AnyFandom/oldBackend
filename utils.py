# utils.py

from flask import jsonify
from flask_restful import fields


class UserIdField(fields.Raw):
    def format(self, value):
        return {
            'id': value.id,
        }


class PostIdField(fields.Raw):
    def format(self, value):
        return {
            'id': value.id,
        }


class CommendIdField(fields.Raw):
    def format(self, value):
        return {
            'id': value.id,
        }

user_marshaller = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'avatar': fields.String,
    'description': fields.String,
    'user_salt': fields.String
}

post_marshaller = {
    'id': fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'owner': UserIdField,
    'date': fields.DateTime(dt_format='iso8601')
}

comment_marshaller = {
    'id': fields.Integer,
    'parent_id': fields.Integer,
    'post': PostIdField,
    'owner': UserIdField,
    'content': fields.String,
    'date': fields.DateTime(dt_format='iso8601')
}

# token_marshaller = {
#     'token': fields.String
# }


def jsend(f):
    def wrapper(*args, **kwargs):
        raw = f(*args, **kwargs)  # ("success", {"token": "eyJhbGciOiJIUzI1NiIsIn"}, 201)
        if not raw:
            return None
        r = {'status': raw[0], 'data' if raw[0] != 'error' else 'message': raw[1]}
        return r, raw[2] if len(raw) > 2 else 200
    return wrapper


def parser(dictionary, *args):  # (name, type, required)
    resp = {}
    for arg in args:
        item = dictionary.get(arg[0])
        if arg[2] and (item is None or type(item) != arg[1]):  # if required and (no such item or item is wrong type)
            return None
        elif not arg[2] and (item is None or type(item) != arg[1]):  # if not required and (no such item or item is wrong type)
            continue
        else:
            resp[arg[0]] = dictionary[arg[0]]

    return resp


def error(code, json=False):
    errors = {
        # AUTH
        'E1001': ['Token is invalid.', 403],
        'E1002': ['Incorrect username or password.', 403],
        # POSTS
        'E1011': ['You are not the author of this post.', 403],
        # COMMENTS
        'E1021': ['You are not the author of the comment', 403],
        # OTHER
        'E1101': ['One or multiple required parameters were not transferred or invalid.', 400],
        'E1102': ['You don\'t have sufficent permissions to access this page.', 403]
    }
    if not json:
        return 'fail', {'code': code, 'message': errors[code][0]}, errors[code][1]
    else:
        return jsonify({'status': 'fail', 'data': {'code': code, 'message': errors[code][0]}}), errors[code][1]
