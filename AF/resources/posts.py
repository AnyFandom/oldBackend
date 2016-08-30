import pickle
from datetime import datetime

from flask import g, url_for
from flask_restful import Resource, abort, marshal
from flask_restful.reqparse import RequestParser

from pony import orm

from AF import db

from AF.utils import authorized, error, jsend
from AF.models import Post, Comment
from AF.marshallers import post_marshaller, comment_marshaller


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

        return 'success', None, 201

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

        return 'success', None, 202


class PostCommentList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            abort(404)

        return 'success', {'comments': marshal(list(Comment.select(lambda p: p.post == post)[:]), comment_marshaller)}
