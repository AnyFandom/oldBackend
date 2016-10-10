import pickle

from flask import g, url_for
from flask_restful import Resource, marshal

from pony import orm

from AF import app, db

from AF.utils import authorized, Error, jsend, parser, between
from AF.models import Post, Comment
from AF.marshallers import comment_marshaller

from AF.socket_utils import send_update, send_notification


class CommentList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            raise Error('E1102')

        args = parser(g.args,
            ('post', int, True),
            ('parent', int, False),
            ('content', str, True))
        if not args:
            raise Error('E1101')

        try:
            post = Post[args['post']]
            parent = None if not args.get('parent', None) else Comment[args['parent']]
        except (orm.core.ObjectNotFound, KeyError):
            raise Error('E1101')

        if parent:
            if parent.post != post:
                raise Error('E1101')

        depth = 0 if parent is None else (parent.depth + 1)

        content = between(args['content'], app.config['MIN_MAX']['comment_content'], 'E1072')
        comment = Comment(post=post, parent=parent, depth=depth, content=content, owner=pickle.loads(g.user))

        db.commit()

        send_update('comment-list', post.id)
        if parent:
            print('Notification!')
            send_notification('New answer', 'New answer! ' + comment.content, comment.parent.owner.id)
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
            raise Error('E1073')

    @jsend
    @orm.db_session
    def delete(self, id):
        try:
            comment = Comment[id]
        except orm.core.ObjectNotFound:
            raise Error('E1073')

        if not authorized():
            raise Error('E1102')

        if comment.owner != pickle.loads(g.user):
            raise Error('E1102')

        comment.delete()
        db.commit()
        send_update('comment-list', comment.post.id)
        send_update('comment', comment.id)

        return 'success', None, 201

    @jsend
    @orm.db_session
    def patch(self, id):
        try:
            comment = Comment[id]
        except orm.core.ObjectNotFound:
            raise Error('E1073')

        if not authorized():
            raise Error('E1102')

        if comment.owner != pickle.loads(g.user):
            raise Error('E1102')

        # parser = RequestParser()
        # parser.add_argument('content', type=str, required=True)
        # args = parser.parse_args()
        args = parser(g.args,
            ('content', str, True))
        if not args:
            raise Error('E1101')

        comment.content = between(args['content'], app.config['MIN_MAX']['comment_content'], 'E1072')

        db.commit()
        send_update('comment-list', comment.post.id)
        send_update('comment', comment.id)

        return 'success', None, 200
