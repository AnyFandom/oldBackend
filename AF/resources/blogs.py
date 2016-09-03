import pickle

from flask import g, url_for
from flask_restful import Resource, abort, marshal

from pony import orm

from AF import db

from AF.utils import authorized, error, jsend, parser
from AF.models import Fandom, Blog, Post
from AF.marshallers import blog_marshaller, post_marshaller


class BlogList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized('user'):
            return error('E1102')

        args = parser(g.args,
            ('title', str, True),
            ('description', str, False),
            ('avatar', str, False),
            ('fandom', int, True))
        if not args:
            return error('E1101')

        try:
            fandom = Fandom[args['fandom']]
        except orm.code.ObjectNotFound:
            return error('E1101')

        blog = Blog(title=args['title'], fandom=fandom, owner=pickle.loads(g.user))
        if args.get('description', None):
            blog.description = args['description']
        if args.get('avatar', None):
            blog.avatar = args['avatar']

        db.commit()

        return 'success', {'Location': url_for('blogitem', id=blog.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'blogs': marshal(list(Blog.select()[:]), blog_marshaller)}


class BlogItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            return 'success', {'blog': marshal(Blog[id], blog_marshaller)}
        except orm.core.ObjectNotFound:
            abort(404)

    @jsend
    @orm.db_session
    def delete(self, id):
        try:
            blog = Blog[id]
        except orm.core.ObjectNotFound:
            abort(404)

        if not authorized('sadmin', 'smoder', 'fadmin', 'fmoder', fandom=blog.fandom, owner=pickle.loads(g.user)):
            return error('E1102')

        blog.delete()
        db.commit()

        return 'success', None, 201

    @jsend
    @orm.db_session
    def patch(self, id):
        try:
            blog = Blog[id]
        except orm.code.ObjectNotFound:
            return abort(404)

        if not authorized('sadmin', 'smoder', 'fadmin', 'fmoder', 'badmin', fandom=blog.fandom, blog=blog, owner=pickle.loads(g.user)):
            return error('E1102')

        args = parser(g.args,
            ('title', str, False),
            ('description', str, False),
            ('avatar', str, False))

        if args.get('title'):
            blog.title = args['title']
        if args.get('description'):
            blog.description = args['description']
        if args.get('avatar'):
            blog.description = args['avatar']

        db.commit()

        return 'success', None, 202


class BlogPostList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            blog = Blog[id]
        except orm.core.ObjectNotFound:
            abort(404)

        return 'success', {'posts': marshal(list(Post.select(lambda p: p.blog == blog)), post_marshaller)}
