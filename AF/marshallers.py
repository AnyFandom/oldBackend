from flask_restful import fields


class UserField(fields.Raw):
    def format(self, value):
        return {
            'id': value.id,
            'username': value.username,
            'avatar': value.avatar
        }

class FandomField(fields.Raw):
    def format(self, value):
        return {
            'id': value.id,
            'title': value.title,
            'avatar': value.avatar
        }

class BlogField(fields.Raw):
    def format(self, value):
        return {
            'id': value.id,
            'title': value.title,
            'avatar': value.avatar,
            'fandom': FandomField.format(None, value.fandom)
        }


class IdField(fields.Raw):
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
    'preview_image': fields.String,
    'owner': UserField,
    'comment_count': fields.Integer,
    'date': fields.DateTime(dt_format='iso8601'),
    'blog': BlogField
}

comment_marshaller = {
    'id': fields.Integer,
    'content': fields.String,
    'parent': IdField,
    'depth': fields.Integer,
    'post': IdField,
    'owner': UserField,
    'date': fields.DateTime(dt_format='iso8601')
}

fandom_marshaller = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'avatar': fields.String
}

blog_marshaller = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'avatar': fields.String,
    'fandom': FandomField,
    'owner': UserField
}
