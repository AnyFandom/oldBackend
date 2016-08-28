# resources.py

import pickle
import random
import string

from flask import g, request, url_for
from flask_restful import Resource, abort, marshal
from flask_restful.reqparse import RequestParser

from utils import *
from models import *
from authentication import *


class Test(Resource):
    def post(self):
        print(request.values.to_dict())
        abort(500)


class Token(Resource):
    @jsend
    @orm.db_session
    def post(self):
        parser = RequestParser(bundle_errors=True)
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        user = User.select(lambda p: p.username == args['username'])[:]
        if not user or not user[0].password == args['password']:
            return error('E1002')

        token = generate_token(user[0].id, user[0].user_salt)
        if not token:
            return 'error', 'Failed to generate token', 500

        return 'success', {'token': str(token, 'utf8')}, 201


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
        user = User(username=args.username, password=args.password, user_salt=salt)
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
        try:
            return 'success', {'user': marshal(User[id], user_marshaller)}
        except orm.core.ObjectNotFound:
            abort(404)


class UserPostList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            user = User[id]
        except orm.core.ObjectNotFound:
            abort(404)

        return 'success', {'posts': marshal(list(Post.select(lambda p: p.owner == user)[:]), post_marshaller)}


class UserCommentList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            user = User[id]
        except orm.core.ObjectNotFound:
            abort(404)

        return 'success', {'comments': marshal(list(Comment.select(lambda p: p.owner == user)[:]), post_marshaller)}


class PostList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            return error('E1102')

        parser = RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('content', type=str, required=True)
        args = parser.parse_args()

        post = Post(title=args['title'], content=args['content'], owner=pickle.loads(g.user), date=datetime.utcnow())

        db.commit()

        return 'success', {'Location': url_for('postitem', id=post.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'posts': marshal(list(Post.select()[:]), post_marshaller)}


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
            return error('E1102')

        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            abort(404)

        if post.owner != pickle.loads(g.user):
            return error('E1011')

        post.delete()
        db.commit()

        return 'success', {}, 201

    @jsend
    @orm.db_session
    def patch(self, id):
        if not authorized():
            return error('E1102')
        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            abort(404)

        if post.owner != pickle.loads(g.user):
            return error('E1011')

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


class PostCommentList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            abort(404)

        return 'success', {'comments': marshal(list(Comment.select(lambda p: p.post == post)[:]), comment_marshaller)}


class CommentList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            return error('E1102')

        parser = RequestParser()
        parser.add_argument('post', type=int, required=True)
        parser.add_argument('parent_id', type=int, required=True)
        parser.add_argument('content', type=str, required=True)
        args = parser.parse_args()

        post = Post.select(lambda p: p.id == args['post'])[:]
        if not post:
            return error('E1101')

        comment = Comment(post=post[0], parent_id=args['parent_id'], content=args['content'], owner=pickle.loads(g.user), date=datetime.utcnow())

        db.commit()

        return 'success', {'Location': url_for('commentitem', id=comment.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'comments': marshal(list(Comment.select()[:]), comment_marshaller)}


class CommentItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            return 'success', {'comment': marshal(Comment[id], comment_marshaller)}
        except orm.core.ObjectNotFound:
            abort(404)

    @jsend
    @orm.db_session
    def delete(self, id):
        if not authorized():
            return error('E1102')

        try:
            comment = Comment[id]
        except orm.core.ObjectNotFound:
            abort(404)

        if comment.owner != pickle.loads(g.user):
            return error('E1021')

        comment.delete()
        db.commit()

        return 'success', {}, 201

    @jsend
    @orm.db_session
    def patch(self, id):
        if not authorized():
            return error('E1102')

        try:
            comment = Comment[id]
        except orm.core.ObjectNotFound:
            abort(404)

        if comment.owner != pickle.loads(g.user):
            return error('E1021')

        parser = RequestParser()
        parser.add_argument('content', type=str, required=True)
        args = parser.parse_args()

        comment.content = args['content']

        db.commit()

        return 'success', {}, 202
