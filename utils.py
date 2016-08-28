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
        return jsonify(r), raw[2] if len(raw) > 2 else 200
    return wrapper
