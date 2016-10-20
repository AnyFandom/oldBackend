from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import app, db

from AF.utils import authorized, Error, jsend, parser, between
from AF.models import Fandom, Post
from AF.marshallers import FandomSchema
from AF.socket_utils import send_update


class FandomList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            raise Error('E1102')

        args = parser(g.args,
            ('title', str, True),
            ('description', str, False),
            ('avatar', str, False))
        if not args:
            raise Error('E1101')

        title = between(args['title'], app.config['MIN_MAX']['fandom_title'], 'E1042')
        fandom = Fandom(title=title)

        if args.get('description', None):
            fandom.description = between(args['description'], app.config['MIN_MAX']['fandom_description'], 'E1043')
        if args.get('avatar', None):
            fandom.avatar = args['avatar']

        try:
            db.commit()
            send_update('fandom-list')
        except orm.core.TransactionIntegrityError:
            raise Error('E1041')

        return 'success', {'Location': url_for('fandomitem', id=fandom.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'fandoms': FandomSchema(many=True).dump(Fandom.select()).data}


class FandomItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            return 'success', {'fandom': FandomSchema().dump(Fandom[id]).data}
        except orm.core.ObjectNotFound:
            raise Error('E1044')

    @jsend
    @orm.db_session
    def delete(self, id):
        try:
            fandom = Fandom[id]
        except orm.core.ObjectNotFound:
            raise Error('E1044')

        if not authorized():
            raise Error('E1102')

        fandom.delete()
        db.commit()
        send_update('fandom-list')
        send_update('fandom', fandom.id)

        return 'success', None, 201

    @jsend
    @orm.db_session
    def patch(self, id):
        try:
            fandom = Fandom[id]
        except orm.code.ObjectNotFound:
            raise Error('E1044')

        if not authorized():
            raise Error('E1102')

        args = parser(g.args,
            ('title', str, False),
            ('description', str, False),
            ('avatar', str, False))

        if args.get('title'):
            fandom.title = between(args['title'], app.config['MIN_MAX']['fandom_title'], 'E1042')
        if args.get('description'):
            fandom.description = between(args['description'], app.config['MIN_MAX']['fandom_description'], 'E1043')
        if args.get('avatar'):
            fandom.avatar = args['avatar']

        db.commit()
        send_update('fandom-list')
        send_update('fandom', fandom.id)

        return 'success', None, 200


class FandomBlogList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            fandom = Fandom[id]
        except orm.core.ObjectNotFound:
            raise Error('E1044')

        return 'success', {'blogs': FandomSchema(many=True).dump(fandom.blogs.select()).data}


class FandomPostList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            fandom = Fandom[id]
        except orm.core.ObjectNotFound:
            raise Error('E1044')
        fandom_blogs = fandom.blogs.select()
        return 'success', {'posts': FandomSchema(many=True).dump(Post.select(lambda p: p.blog in fandom_blogs)).data}
