from marshmallow import Schema, SchemaOpts, fields, post_load, validate
from AF import app  # , ma
from AF.models import User, Fandom, Blog, Post, Comment
from AF.utils import Error


class NamespaceOpts(SchemaOpts):
    def __init__(self, meta):
        SchemaOpts.__init__(self, meta)
        self.model = getattr(meta, 'model', None)


class NamespacedSchema(Schema):
    OPTIONS_CLASS = NamespaceOpts

    def handle_error(self, exc, data):
        print(exc.messages)
        raise Error('E1101', exc.messages)

    @post_load(pass_many=True)
    def make_object(self, data, many):
        return self.opts.model(**data)

# TODO: Не надо возвращать все, только некоторые поля


class UserSchema(NamespacedSchema):
    id = fields.Integer(dump_only=True)
    username = fields.String(validate=validate.Length(**app.config['MIN_MAX']['username']), required=True)
    password = fields.String(validate=validate.Length(**app.config['MIN_MAX']['password']), required=True, load_only=True)
    description = fields.String(validate=validate.Length(**app.config['MIN_MAX']['user_description']))
    avatar = fields.Url()
    user_salt = fields.String(load_only=True)
    registration_date = fields.DateTime()

    class Meta:
        model = User


class FandomSchema(NamespacedSchema):
    id = fields.Integer(dump_only=True)
    title = fields.String(validate=validate.Length(**app.config['MIN_MAX']['fandom_title']), required=True)
    description = fields.String(validate=validate.Length(**app.config['MIN_MAX']['fandom_description']))
    avatar = fields.Url()

    class Meta:
        model = Fandom


class BlogSchema(NamespacedSchema):
    id = fields.Integer(dump_only=True)
    title = fields.String(validate=validate.Length(**app.config['MIN_MAX']['blog_title']), required=True)
    description = fields.String(validate=validate.Length(**app.config['MIN_MAX']['blog_description']))
    avatar = fields.Url()
    owner = fields.Nested(UserSchema)
    fandom = fields.Nested(FandomSchema)

    class Meta:
        model = Blog


class PostSchema(NamespacedSchema):
    id = fields.Integer(dump_only=True)
    title = fields.String(validate=validate.Length(**app.config['MIN_MAX']['post_title']), required=True)
    content = fields.String(validate=validate.Length(**app.config['MIN_MAX']['post_content']), required=True)
    preview_image = fields.Url()
    owner = fields.Nested(UserSchema)
    comment_count = fields.Integer()
    date = fields.DateTime()
    blog = fields.Nested(BlogSchema)

    class Meta:
        model = Post


class CommentSchema(NamespacedSchema):
    id = fields.Integer(dump_only=True)
    content = fields.String(validate=validate.Length(**app.config['MIN_MAX']['comment_content']), required=True)
    parent = fields.Nested('CommentSchema')
    depth = fields.Integer()
    post = fields.Nested(PostSchema)
    owner = fields.Nested(UserSchema)
    date = fields.DateTime()

    class Meta:
        model = Comment
