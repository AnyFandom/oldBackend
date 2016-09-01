from flask_restful import fields


class UserField(fields.Raw):
    def format(self, value):
        return {
            'id': value.id,
            'username': value.username,
            'avatar': value.avatar
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
    'owner': UserField,
    'date': fields.DateTime(dt_format='iso8601')
}

comment_marshaller = {
    'id': fields.Integer,
    'content': fields.String,
    'parent': CommendIdField,
    'depth': fields.Integer,
    'post': PostIdField,
    'owner': UserField,
    'date': fields.DateTime(dt_format='iso8601')
}
