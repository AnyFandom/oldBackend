import pickle

from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import db

from AF.utils import authorized, Error, jsend, nparser
from AF.models import Comment
from AF.marshallers import CommentSchema

from AF.socket_utils import send_update, send_notification


def get_comment(id):
    try:
        return Comment[id]
    except orm.core.ObjectNotFound:
        raise Error('E1075')


class CommentList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            raise Error('E1102')

        args = nparser(g.args, ['post', 'parent', 'content'])
        comment = Comment(**CommentSchema().load(
            {**args, 'owner': pickle.loads(g.user)}
        ).data)

        db.commit()

        send_update('comment-list', comment.post.id)
        if comment.parent:
            print('Notification!')
            send_notification('New answer', 'New answer! ' + comment.content, comment.parent.owner.id)
        return 'success', {'Location': url_for('commentitem', id=comment.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'comments': CommentSchema(many=True).dump(Comment.select()).data}


class CommentItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        return 'success', {'comment': CommentSchema().dump(get_comment(id)).data}

    @jsend
    @orm.db_session
    def delete(self, id):
        comment = get_comment(id)

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
        comment = get_comment(id)

        if not authorized():
            raise Error('E1102')

        if comment.owner != pickle.loads(g.user):
            raise Error('E1102')

        # parser = RequestParser()
        # parser.add_argument('content', type=str, required=True)
        # args = parser.parse_args()

        # args = parser(g.args,
        #     ('content', str, True))
        # if not args:
        #     raise Error('E1101')

        args = nparser(g.args, ['content'])
        changes = CommentSchema(partial=True).load(args).data

        if changes.get('content'):
            comment.content = changes['content']

        db.commit()
        send_update('comment-list', comment.post.id)
        send_update('comment', comment.id)

        return 'success', None, 200
