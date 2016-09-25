import pickle

from flask import g, url_for
from flask_restful import Resource, abort, marshal

from pony import orm

from AF import app, db

from AF.utils import jsend, Error, parser, between
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
            raise Error('E1101')

        username = between(args['username'], app.config['MIN_MAX']['username'], 'E1032')
        password = between(args['password'], app.config['MIN_MAX']['password'], 'E1033')
        user = User(username=username, password=password)

        if args.get('description', None):
            user.description = between(args['description'], app.config['MIN_MAX']['user_description'], 'E1034')
        if args.get('avatar', None):
            user.avatar = args['avatar']

        try:
            db.commit()
        except orm.core.TransactionIntegrityError:
            raise Error('E1031')

        return 'success', {'Location': url_for('useritem', id=user.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'users': marshal(list(User.select()[:]), user_marshaller)}


class UserItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id=None, username=None):
        if not (id or username):  # /users/current
            if g.get('user', None):
                return 'success', {'user': marshal(pickle.loads(g.user), user_marshaller)}
            else:
                raise Error('E1003')
        else:  # /users/id/<int:id> or /users/profile/<string:username>
            try:
                user = User[id] if id else User.get(username=username)
                if not user:
                    raise ValueError

                return 'success', {'user': marshal(user, user_marshaller)}  # if id is not None then /users/id else /users/profile
            except (orm.core.ObjectNotFound, ValueError):
                abort(404)


class UserPostList(Resource):
    @jsend
    @orm.db_session
    def get(self, id=None, username=None):
        if not (id or username):
            if g.get('user', None):
                return 'success', {'posts': marshal(list(Post.select(lambda p: p.owner == pickle.loads(g.user))[:]), post_marshaller)}
            else:
                raise Error('E1003')
        else:
            try:
                user = User[id] if id else User.get(username=username)  # Вынес в отдельную переменную из-за ошибки NotImplementedError
                if not user:
                    raise ValueError

                return 'success', {'posts': marshal(list(Post.select(lambda p: p.owner == user)), post_marshaller)}
            except (orm.core.ObjectNotFound, orm.core.ExprEvalError, ValueError):
                abort(404)


class UserCommentList(Resource):
    @jsend
    @orm.db_session
    def get(self, id=None, username=None):
        if not (id or username):
            if g.get('user', None):
                return 'success', {'comments': marshal(list(Comment.select(lambda p: p.owner == pickle.loads(g.user))[:]), comment_marshaller)}
            else:
                raise Error('E1003')
        else:
            try:
                user = User[id] if id else User.get(username=username)
                if not user:
                    raise ValueError

                return 'success', {'comments': marshal(list(Comment.select(lambda p: p.owner == user)), comment_marshaller)}
            except (orm.core.ObjectNotFound, orm.core.ExprEvalError, ValueError):
                abort(404)
