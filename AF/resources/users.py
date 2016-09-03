import pickle

from flask import g, url_for
from flask_restful import Resource, abort, marshal

from pony import orm

from AF import db

from AF.utils import jsend, authorized, error, parser
from AF.models import Comment, Post, User
from AF.marshallers import user_marshaller, post_marshaller, comment_marshaller


class UserList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        args = parser(g.args,
            ('username', str, True),
            ('password', str, True),
            ('avatar', str, False),
            ('description', str, False))
        if not args:
            return error('E1101')

        user = User(username=args['username'], password=args['password'])
        if args.get('avatar', None):
            user.avatar = args['avatar']
        if args.get('description', None):
            user.description = args['description']

        db.commit()

        return 'success', {'Location': url_for('useritem', id=user.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'users': marshal(list(User.select()[:]), user_marshaller)}


class UserItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        if id == 'current':
            if authorized():
                return 'success', {'user': marshal(pickle.loads(g.user), user_marshaller)}
            else:
                return error('E1003')
        else:
            try:
                return 'success', {'user': marshal(User[id], user_marshaller)}
            except (orm.core.ObjectNotFound, ValueError):
                abort(404)


class UserPostList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        if id == 'current':
            if authorized():
                return 'success', {'posts': marshal(list(Post.select(lambda p: p.owner == pickle.loads(g.user))[:]), post_marshaller)}
            else:
                return error('E1003')
        else:
            try:
                return 'success', {'posts': marshal(list(Post.select(lambda p: p.owner == User[id])[:]), post_marshaller)}
            except (orm.core.ObjectNotFound, orm.core.ExprEvalError):
                abort(404)


class UserCommentList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        if id == 'current':
            if authorized():
                return 'success', {'comments': marshal(list(Comment.select(lambda p: p.owner == pickle.loads(g.user))[:]), comment_marshaller)}
            else:
                return error('E1003')
        else:
            try:
                return 'success', {'comments': marshal(list(Comment.select(lambda p: p.owner == User[id])[:]), comment_marshaller)}
            except (orm.core.ObjectNotFound, orm.core.ExprEvalError):
                abort(404)
