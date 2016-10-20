from marshmallow import validate, ValidationError, post_load, Schema
from marshmallow.fields import Nested, Integer, String, DateTime, Url
from pony import orm

from AF import app  # , ma
from AF.models import User, Fandom, Blog, Post, Comment
from AF.utils import Error


class CValidationError(ValidationError):
    def __init__(self, message, field="_schema", **kwargs):
        self.field = field
        super(CValidationError, self).__init__(**kwargs, message=message)

    def normalized_messages(self):
        if isinstance(self.messages, dict):
            return self.messages
        if len(self.field_names) == 0:
            return {self.field: self.messages}
        return dict((name, self.messages) for name in self.field_names)


class CNested(Nested):
    def __init__(self, object, nested, **kwargs):
        self.object = object
        super(CNested, self).__init__(**kwargs, nested=nested)

    def _deserialize(self, value, attr, data):
        try:
            if value in [0, '0']:
                return None
            if not isinstance(value, self.object):
                value = self.object[value]
        except (orm.core.ObjectNotFound, ValueError):
            raise CValidationError('Object with specified ID doesn\'t exists.')

        return value


class TopSchema(Schema):
    id = Integer(dump_only=True)
    created_at = DateTime(dump_only=True)

    def handle_error(self, exc, data):
        raise Error('E1101', exc.messages)


# TODO: Не надо возвращать все, только некоторые поля
# NOTE: Не ставить default в схемы


class UserSchema(TopSchema):
    username = String(validate=validate.Length(**app.config['MIN_MAX']['username']), required=True)
    password = String(validate=validate.Length(**app.config['MIN_MAX']['password']), required=True, load_only=True)
    description = String(validate=validate.Length(**app.config['MIN_MAX']['user_description']))
    avatar = String()
    user_salt = String(load_only=True)

    # links = ma.Hyperlinks({
    #     'self': [
    #         ma.URLFor('useritem', id='<id>'),
    #         ma.URLFor('useritem', username='<username>')
    #     ],
    #     'blogs': [
    #         ma.URLFor('userbloglist', id='<id>'),
    #         ma.URLFor('userbloglist', username='<username>')
    #     ],
    #     'posts': [
    #         ma.URLFor('userpostlist', id='<id>'),
    #         ma.URLFor('userpostlist', username='<username>')
    #     ],
    #     'comments': [
    #         ma.URLFor('usercommentlist', id='<id>'),
    #         ma.URLFor('usercommentlist', username='<username>')
    #     ],
    # })


class FandomSchema(TopSchema):
    title = String(validate=validate.Length(**app.config['MIN_MAX']['fandom_title']), required=True)
    description = String(validate=validate.Length(**app.config['MIN_MAX']['fandom_description']))
    avatar = String()

    # links = ma.Hyperlinks({
    #     'self': ma.URLFor('fandomitem', id='<id>'),
    #     'blogs': ma.URLFor('fandombloglist', id='<id>'),
    #     'posts': ma.URLFor('fandompostlist', id='<id>')
    # })


class BlogSchema(TopSchema):
    title = String(validate=validate.Length(**app.config['MIN_MAX']['blog_title']), required=True)
    description = String(validate=validate.Length(**app.config['MIN_MAX']['blog_description']))
    avatar = String()
    owner = CNested(User, UserSchema, required=True, only=['id', 'username', 'avatar'])
    fandom = CNested(Fandom, FandomSchema, required=True, only=['id', 'title', 'avatar'])

    # links = ma.Hyperlinks({
    #     'self': ma.URLFor('blogitem', id='<id>'),
    #     'posts': ma.URLFor('blogpostlist', id='<id>')
    # })


class PostSchema(TopSchema):
    title = String(validate=validate.Length(**app.config['MIN_MAX']['post_title']), required=True)
    content = String(validate=validate.Length(**app.config['MIN_MAX']['post_content']), required=True)
    preview_image = String()
    comment_count = Integer()
    owner = CNested(User, UserSchema, required=True, only=['id', 'username', 'avatar'])
    blog = CNested(Blog, BlogSchema, required=True, only=['id', 'title', 'avatar'])

    # links = ma.Hyperlinks({
    #     'self': ma.URLFor('postitem', id='<id>'),
    #     'comments': ma.URLFor('postcommentlist', id='<id>')
    # })


class CommentSchema(TopSchema):
    content = String(validate=validate.Length(**app.config['MIN_MAX']['comment_content']), required=True)
    parent = CNested(Comment, 'self', only=['id', 'content', 'depth', 'owner'])
    depth = Integer()
    post = CNested(Post, PostSchema, required=True, only=['id', 'title'])
    owner = CNested(User, UserSchema, required=True, only=['id', 'username', 'avatar'])

    # links = ma.Hyperlinks({
    #     'self': ma.URLFor('commentitem', id='<id>')
    # })

    @post_load
    def parent_check(self, data):
        if data.get('parent'):
            data['depth'] = data['parent'].depth + 1
            if data['post'] != data['parent'].post:
                raise CValidationError('Parent is not in same post as new comment.', 'parent')
        else:
            data['depth'] = 0
