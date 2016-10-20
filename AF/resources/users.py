import pickle

from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import app, db

from AF.utils import jsend, Error, parser, between, authorized
from AF.models import User
from AF.marshallers import UserSchema, PostSchema, CommentSchema
from AF.socket_utils import send_update


def get_user(id, username):
    if not (id or username):  # /users/current
        if g.get('user', None):
            return pickle.loads(g.user)
        else:
            raise Error('E1003')
    else:  # /users/id/<int:id> or /users/profile/<string:username>
        try:
            user = User[id] if id else User.get(username=username)
            if not user:
                raise ValueError

            return user
        except (orm.core.ObjectNotFound, orm.core.ExprEvalError, ValueError):
            raise Error('E1035')


class UserList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        user = UserSchema().load(g.args).data

        try:
            db.commit()
            send_update('user-list')
        except orm.core.TransactionIntegrityError:
            raise Error('E1031')

        return 'success', {'Location': url_for('useritem', id=user.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'users': UserSchema(many=True).dump(User.select()).data}


class UserItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id=None, username=None):
        user = get_user(id, username)
        return 'success', {'user': UserSchema().dump(user).data}

    @jsend
    @orm.db_session
    def delete(self, id=None, username=None):
        user = get_user(id, username)

        if not authorized():
            raise Error('E1102')

        # if user != pickle.loads(g.user):
        #    raise Error('E1102')

        user.delete()
        db.commit()
        send_update('user-list')
        send_update('user', user.id)

        return 'success', None, 200

    @jsend
    @orm.db_session
    def patch(self, id=None, username=None):
        user = get_user(id, username)

        if not authorized():
            raise Error('E1102')

        if user != pickle.loads(g.user):
            raise Error('E1102')

        args = parser(g.args,
            ('password', str, False),
            ('new_password', str, False),
            ('avatar', str, False),
            ('description', str, False))

        if args.get('new_password'):
            if user.check_password(args.get('password')):
                user.password = between(args['new_password'], app.config['MIN_MAX']['password'], 'E1033')
            else:
                raise Error('E1036')
        if args.get('description'):
            user.description = between(args['description'], app.config['MIN_MAX']['user_description'], 'E1034')
        if args.get('avatar'):
            user.avatar = args['avatar']

        db.commit()
        send_update('user-list')
        send_update('user', user.id)

        return 'success', None, 201


class UserPostList(Resource):
    @jsend
    @orm.db_session
    def get(self, id=None, username=None):
        user = get_user(id, username)
        return 'success', {'posts': PostSchema(many=True).dump(user.posts.select()).data}


class UserCommentList(Resource):
    @jsend
    @orm.db_session
    def get(self, id=None, username=None):
        user = get_user(id, username)
        return 'success', {'comments': CommentSchema(many=True).dump(user.comments.select()).data}
