import pickle
from datetime import datetime

from flask import g, url_for
from flask_restful import Resource, abort, marshal

from pony import orm

from AF import db

from AF.utils import authorized, error, jsend, parser
from AF.models import Post, Comment
from AF.marshallers import comment_marshaller

from AF.socket_utils import send_update_comments_request, send_notification


class CommentList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            return error('E1102')

        args = parser(g.args,
            ('post', int, True),
            ('parent', int, False),
            ('content', str, True))
        if not args:
            return error('E1101')

        try:
            post = Post[args['post']]
            parent = None if not args.get('parent', None) else Comment[args['parent']]
        except (orm.core.ObjectNotFound, KeyError):
            return error('E1101')

        if parent:
            if parent.post != post:
                return error('E1101')

        depth = 0 if parent is None else (parent.depth + 1)

        comment = Comment(post=post, parent=parent, depth=depth, content=args['content'], owner=pickle.loads(g.user))

        db.commit()

        send_update_comments_request(post.id)
        if parent:
            print('Notification!')
            send_notification('New answer', 'New answer to you!' + comment.content, comment.parent.owner.id)
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

        return 'success', None, 201

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

        # parser = RequestParser()
        # parser.add_argument('content', type=str, required=True)
        # args = parser.parse_args()
        args = parser(g.args,
            ('content', str, True))
        if not args:
            return error('E1101')

        comment.content = args['content']

        db.commit()

        return 'success', None, 202
