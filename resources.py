# resources.py

import random
import string

from flask_restful import Resource, marshal, abort
from flask_restful.reqparse import RequestParser
from flask import url_for, g

from models import *
from utils import *
from authentication import *


class Token(Resource):
    @jsend
    @orm.db_session
    def post(self):
        parser = RequestParser()
        parser.add_argument('username', type=str, required=False)
        parser.add_argument('password', type=str, required=False)
        args = parser.parse_args()

        if args.get('username', None) and args.get('password', None):
            auth = {'username': args['username'], 'password': args['password']}
        else:
            return 'fail', {'message': 'Please enter username and password'}, 403

        u = User.select(lambda p: p.username == auth['username'])[:]
        if not u or not u[0].password == auth['password']:
            return 'fail', {'message': 'Incorrect username or password'}, 403

        token = generate_token(u[0].id, u[0].user_salt)
        if not token:
            return 'error', 'Failed to generate token', 500

        return 'success', {'token': str(token, 'utf8')}, 201


class UserItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            return 'success', {'user': marshal(User[id], user_marshaller)}
        except orm.core.ObjectNotFound:
            abort(404)


class UserList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        parser = RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('avatar', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        args = parser.parse_args()

        salt = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))
        u = User(username=args.username, password=args.password, user_salt=salt)
        if args.get('avatar', None):
            u.avatar = args['avatar']
        if args.get('description', None):
            u.description = args['description']

        db.commit()

        return 'success', {'Location': url_for('useritem', id=u.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'users': marshal(list(User.select()[:]), user_marshaller)}


class Test(Resource):
    def post(self):
        abort(500)


class PostList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        parser = RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        args = parser.parse_args()

        post = Post(title=args['title'], content=args['content'], owner=g.user)
        db.commit()

        return 'success', {'Location': url_for('postitem', id=post.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'post': marshal(list(Post.select()[:]), post_marshaller)}


class PostItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            return 'success', {'post': marshal(Post[id], post_marshaller)}
        except orm.core.ObjectNotFound:
            abort(404)

    @jsend
    @orm.db_session
    def delete(self, id):
        if not authorized():
            return 'fail', {'message': 'You dont have sufficent permissions to access this page'}, 403

        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            abort(404)

        if post.owner != g.user:
            return 'fail', {'message': 'You are not the author of this post.'}, 403

        post.delete()
        db.commit()

        return 'success', {}, 201

    @jsend
    @orm.db_session
    def patch(self, id):
        if not authorized():
            return 'fail', {'message': 'You dont have sufficent permissions to access this page'}, 403
        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            abort(404)

        if post.owner != g.user:
            return 'fail', {'message': 'You are not the author of this post.'}, 403

        parser = RequestParser()
        parser.add_argument('title', type=str, required=False)
        parser.add_argument('content', type=str, required=False)
        args = parser.parse_args()

        if args.get('title'):
            post.title = args['title']

        if args.get('content'):
            post.content = args['content']

        db.commit()

        return 'success', {}, 202
