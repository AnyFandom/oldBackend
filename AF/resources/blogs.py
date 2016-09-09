import pickle

from flask import g, url_for
from flask_restful import Resource, abort, marshal

from pony import orm

from AF import db

from AF.utils import authorized, error, jsend, parser
from AF.models import Staff, User, Fandom, Blog, Post
from AF.marshallers import blog_marshaller, post_marshaller, staff_marshaller


class BlogList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized(0):
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
        return 'success', {'blogs': marshal(list(Blog.select()), blog_marshaller)}


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

        if not authorized(11, 12, 21, 30, fandom=blog.fandom, blog=blog):  # GAdmin, GModer, FAdmin, BOwner
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

        if not authorized(11, 12, 21, 22, 30, 31, fandom=blog.fandom, blog=blog):  # GAdmin, GModer, FOwner, FAdmin, FModer, BOwner, BAdmin
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


class BlogStaffList(Resource):
    @jsend
    @orm.db_session
    def post(self, id):
        try:
            blog = Blog[id]
        except orm.core.ObjectNotFound:
            return abort(404)

        if not authorized(11, 21, 30, 31, blog=blog):
            return error('E1102')

        args = parser(g.args,
            ('user', int, True),
            ('role', int, True))
        if not args:
            return error('E1101')

        try:
            user = User[id]
        except orm.core.ObjectNotFound:
            return error('E1101')

        if args['role'] not in [1, 2]:
            return error('E1101')

        for right in list(user.rights):
            if right.type == 3 and right.role == args['role'] and right.blog == blog:
                return error('E1031' if args['role'] == 1 else 'E1032')

        staff = Staff(user=user, type=3, role=args['role'], blog=blog)
        db.commit()

        return 'success', {'Location': url_for('staffitem', id=staff.id)}, 201

    @jsend
    @orm.db_session
    def get(self, id):
        try:
            blog = Blog[id]
        except orm.core.ObjectNotFound:
            return abort(404)

        return 'success', {'staff': marshal(list(blog.staff), staff_marshaller)}
