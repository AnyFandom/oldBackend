import pickle
import datetime

from flask import g, url_for
from flask_restful import Resource, abort, marshal
from flask_restful.reqparse import RequestParser

from pony import orm

from AF import db

from AF.utils import authorized, error, jsend
from AF.models import Post, Comment
from AF.marshallers import comment_marshaller


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

        post = Post[args['post']]
        if not post:
            return error('E1101')

        comment = Comment(post=post, parent_id=args['parent_id'], content=args['content'], owner=pickle.loads(g.user), date=datetime.utcnow())

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
