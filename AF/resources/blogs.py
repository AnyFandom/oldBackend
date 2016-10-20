import pickle

from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import app, db

from AF.utils import authorized, Error, jsend, parser, between
from AF.models import Fandom, Blog
from AF.marshallers import BlogSchema
from AF.socket_utils import send_update


class BlogList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            raise Error('E1102')

        args = parser(g.args,
            ('title', str, True),
            ('description', str, False),
            ('avatar', str, False),
            ('fandom', int, True))
        if not args:
            raise Error('E1101')

        # TODO: Сделать проверку на уникальность блога в фандоме

        try:
            fandom = Fandom[args['fandom']]
        except orm.core.ObjectNotFound:
            raise Error('E1101')

        title = between(args['title'], app.config['MIN_MAX']['blog_title'], 'E1052')
        blog = Blog(title=title, fandom=fandom, owner=pickle.loads(g.user))

        if args.get('description', None):
            blog.description = between(args['description'], app.config['MIN_MAX']['blog_description'], 'E1053')
        if args.get('avatar', None):
            blog.avatar = args['avatar']

        db.commit()
        send_update('blog-list', fandom.id)

        return 'success', {'Location': url_for('blogitem', id=blog.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'blogs': BlogSchema(many=True).dump(Blog.select()).data}


class BlogItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            return 'success', {'blog': BlogSchema().dump(Blog[id]).data}
        except orm.core.ObjectNotFound:
            raise Error('E1054')

    @jsend
    @orm.db_session
    def delete(self, id):
        try:
            blog = Blog[id]
        except orm.core.ObjectNotFound:
            raise Error('E1054')

        if not authorized():
            raise Error('E1102')

        if blog.owner != pickle.loads(g.user):
            raise Error('E1102')

        blog.delete()
        db.commit()
        send_update('blog-list', blog.fandom.id)

        return 'success', None, 201

    @jsend
    @orm.db_session
    def patch(self, id):
        try:
            blog = Blog[id]
        except orm.code.ObjectNotFound:
            return Error('E1054')

        if not authorized():
            raise Error('E1102')

        if blog.owner != pickle.loads(g.user):
            raise Error('E1102')

        args = parser(g.args,
            ('title', str, False),
            ('description', str, False),
            ('avatar', str, False))

        if args.get('title'):
            blog.title = between(args['title'], app.config['MIN_MAX']['blog_title'], 'E1052')
        if args.get('description'):
            blog.description = between(args['description'], app.config['MIN_MAX']['blog_description'], 'E1053')
        if args.get('avatar'):
            blog.avatar = args['avatar']

        db.commit()
        send_update('blog-list', blog.fandom.id)
        send_update('blog', blog.id)

        return 'success', None, 200


class BlogPostList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            blog = Blog[id]
        except orm.core.ObjectNotFound:
            return Error('E1054')

        return 'success', {'posts': BlogSchema(many=True).dump(blog.posts.select()).data}
