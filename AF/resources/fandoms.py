from flask import g, url_for
from flask_restful import Resource, abort, marshal

from pony import orm

from AF import db

from AF.utils import authorized, error, jsend, parser
from AF.models import Fandom, Blog
from AF.marshallers import fandom_marshaller, blog_marshaller


class FandomList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            return error('E1102')

        args = parser(g.args,
            ('title', str, True),
            ('description', str, False),
            ('avatar', str, False))
        if not args:
            return error('E1101')

        fandom = Fandom(title=args['title'])
        if args.get('description', None):
            fandom.description = args['description']
        if args.get('avatar', None):
            fandom.avatar = args['avatar']

        db.commit()

        return 'success', {'Location': url_for('fandomitem', id=fandom.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'fandoms': marshal(list(Fandom.select()[:]), fandom_marshaller)}


class FandomItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            return 'success', {'fandom': marshal(Fandom[id], fandom_marshaller)}
        except orm.core.ObjectNotFound:
            abort(404)

    @jsend
    @orm.db_session
    def delete(self, id):
        if not authorized():
            return error('E1102')

        try:
            fandom = Fandom[id]
        except orm.core.ObjectNotFound:
            abort(404)

        fandom.delete()
        db.commit()

        return 'success', None, 201

    @jsend
    @orm.db_session
    def patch(self, id):
        if not authorized():
            return error('E1102')

        try:
            fandom = Fandom[id]
        except orm.code.ObjectNotFound:
            return abort(404)

        args = parser(g.args,
            ('title', str, False),
            ('description', str, False),
            ('avatar', str, False))

        if args.get('title'):
            fandom.title = args['title']
        if args.get('description'):
            fandom.description = args['description']
        if args.get('avatar'):
            fandom.description = args['avatar']

        db.commit()

        return 'success', None, 202


class FandomBlogList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            fandom = Fandom[id]
        except orm.core.ObjectNotFound:
            abort(404)

        return 'success', {'blogs': marshal(list(Blog.select(lambda p: p.fandom == fandom)), blog_marshaller)}
