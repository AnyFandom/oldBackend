from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import db

from AF.utils import authorized, Error, jsend, nparser
from AF.models import Fandom, Post
from AF.marshallers import FandomSchema, BlogSchema, PostSchema
from AF.socket_utils import send_update


def get_fandom(id):
    try:
        return Fandom[id]
    except orm.core.ObjectNotFound:
        raise Error('E1045')


class FandomList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            raise Error('E1102')

        args = nparser(g.args, ['title', 'description', 'avatar'])
        fandom = Fandom(**FandomSchema().load(args).data)

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
        return 'success', {'fandom': FandomSchema().dump(get_fandom(id)).data}

    @jsend
    @orm.db_session
    def delete(self, id):
        fandom = get_fandom(id)

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
        fandom = get_fandom(id)

        if not authorized():
            raise Error('E1102')

        args = nparser(g.args, ['title', 'description', 'avatar'])
        changes = FandomSchema(partial=True).load(args).data

        if changes.get('title'):
            fandom.title = changes['title']
        if changes.get('description'):
            fandom.description = changes['description']
        if changes.get('avatar'):
            fandom.avatar = changes['avatar']

        db.commit()
        send_update('fandom-list')
        send_update('fandom', fandom.id)

        return 'success', None, 200


class FandomBlogList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        fandom = get_fandom(id)
        return 'success', {'blogs': BlogSchema(many=True).dump(fandom.blogs.select()).data}


class FandomPostList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        fandom = get_fandom(id)
        fandom_blogs = fandom.blogs.select()
        return 'success', {'posts': PostSchema(many=True).dump(Post.select(lambda p: p.blog in fandom_blogs)).data}
