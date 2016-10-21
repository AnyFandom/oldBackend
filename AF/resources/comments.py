import pickle

from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import db

from AF.utils import authorized, Error, jsend, nparser, get_comments_new
from AF.models import Comment, ReadComments, LastComment
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
        if comment.parent and comment.parent.owner != pickle.loads(g.user):
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
        send_update('comment-list', comment.post.id)
        send_update('comment', comment.id)
        db.commit()

        return 'success', None, 200

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


class CommentReadItem(Resource):

    # TODO: ТЕСТЫ-ТЕСТЫ-ТЕСТЫ

    @jsend
    @orm.db_session
    def post(self, id):
        comment = get_comment(id)
        post = comment.post
        user = pickle.loads(g.user)

        if not authorized():
            raise Error('E1102')

        last_comment = LastComment.select(lambda lc: lc.post==post and lc.user==user).get()

        if last_comment:
            last_comment_id = last_comment.comment.id
        else:
            last_comment_id = 0

        if not list(ReadComments.select(lambda rc: rc.comment == comment and rc.user==user)) and id > last_comment_id:
            rc = ReadComments(comment=comment, user=user, post=post)
            db.commit()

        comments_new = get_comments_new(user, post, last_comment_id)

        if not len(comments_new):
            if last_comment:
                last_comment.comment = comment
            else:
                last_comment = LastComment(post=post, user=user, comment=list(post.comments)[-1])
            orm.delete(rc for rc in ReadComments if rc.post==post and rc.user==user)

        db.commit()
        return 'success', None, 200
