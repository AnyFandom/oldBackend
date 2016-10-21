import pickle
import random
import string

from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import db

from AF.utils import jsend, Error, nparser, authorized
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
        args = nparser(g.args, ['username', 'password', 'description', 'avatar'])
        user = User(**UserSchema().load(args).data)

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

        args = nparser(g.args, ['password_old', 'password', 'avatar', 'description'])
        changes = UserSchema(partial=True).load(args).data  # Вместо кучи вызовов between

        if changes.get('password_hash'):
            if user.check_password(args.get('password_old')):
                user.password_hash = changes['password_hash']
                user.user_salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
            else:
                if not args.get('password_old'):
                    raise Error('E1036')
                else:
                    raise Error('E1004')
        if changes.get('description'):
            user.description = changes['description']
        if changes.get('avatar'):
            user.avatar = changes['avatar']

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
