import pickle

from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import app, db

from AF.utils import authorized, Error, jsend, nparser
from AF.models import Fandom, Blog
from AF.marshallers import UserSchema, FandomSchema, BlogSchema
from AF.socket_utils import send_update


def get_blog(id):
    try:
        return Blog[id]
    except orm.core.ObjectNotFound:
        raise Error('E1055')


class BlogList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        # TODO: Сделать проверку на уникальность блога в фандоме
        if not authorized():
            raise Error('E1102')

        args = nparser(g.args, ['title', 'description', 'avatar', 'fandom'])

        blog = Blog(**BlogSchema().load(
            {**args, 'owner': pickle.loads(g.user)}
        ).data)

        db.commit()
        send_update('blog-list', blog.fandom.id)

        return 'success', {'Location': url_for('blogitem', id=blog.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'blogs': BlogSchema(many=True).dump(Blog.select()).data}


class BlogItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        return 'success', {'blog': BlogSchema().dump(get_blog(id)).data}

    @jsend
    @orm.db_session
    def delete(self, id):
        blog = get_blog(id)

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
        blog = get_blog(id)

        if not authorized():
            raise Error('E1102')

        if blog.owner != pickle.loads(g.user):
            raise Error('E1102')

        args = nparser(g.args, ['title', 'description', 'avatar'])
        changes = BlogSchema(partial=True).load(args).data

        if changes.get('title'):
            blog.title = changes['title']
        if changes.get('description'):
            blog.description = changes['description']
        if changes.get('avatar'):
            blog.avatar = changes['avatar']

        db.commit()
        send_update('blog-list', blog.fandom.id)
        send_update('blog', blog.id)

        return 'success', None, 200


class BlogPostList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        blog = get_blog(id)
        return 'success', {'posts': BlogSchema(many=True).dump(blog.posts.select()).data}
