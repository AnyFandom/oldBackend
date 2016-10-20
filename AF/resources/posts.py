import pickle

from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import db

from AF.utils import authorized, Error, jsend, nparser
from AF.models import Post, Comment, LastComment
from AF.marshallers import PostSchema, CommentSchema
from AF.socket_utils import send_update


def get_post(id):
    try:
        return Post[id]
    except orm.core.ObjectNotFound:
        raise Error('E1065')


class PostList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            raise Error('E1102')

        args = nparser(g.args, ['title', 'content', 'preview_image', 'blog'])

        post = Post(**PostSchema().load(
            {**args, 'owner': pickle.loads(g.user)}
        ).data)

        db.commit()
        send_update('post-list')

        return 'success', {'Location': url_for('postitem', id=post.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'posts': PostSchema(many=True).dump(Post.select()).data}


class PostItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        return 'success', {'post': PostSchema().dump(get_post(id)).data}

    @jsend
    @orm.db_session
    def delete(self, id):
        post = get_post(id)

        if not authorized():
            raise Error('E1102')

        if post.owner != pickle.loads(g.user):
            raise Error('E1102')

        post.delete()
        db.commit()

        return 'success', None, 200

    @jsend
    @orm.db_session
    def patch(self, id):
        post = get_post(id)

        if not authorized():
            raise Error('E1102')

        if post.owner != pickle.loads(g.user):
            raise Error('E1102')

        args = nparser(g.args, ['title', 'content', 'preview_image'])
        changes = PostSchema(partial=True).load(args).data

        if changes.get('title'):
            post.title = changes['title']
        if changes.get('content'):
            post.content = changes['content']
        if changes.get('preview_image'):
            post.preview_image = changes['preview_image']

        db.commit()

        return 'success', None, 200


class PostCommentList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        post = get_post(id)

        args = nparser(g.args, ['threaded'])

        if args.get('threaded', None):
            def recursion(comments):
                resp = []
                for comment in comments:
                    resp.append(comment)
                    resp.extend(recursion(comment.answers.order_by(Comment.id)))
                return resp

            resp = Comment.select(lambda p: p.post == post and p.parent is None)  # Получаем все "корневые" комменты
            resp = recursion(resp)  # Рекурсивно формируем список комментов

            return 'success', {'comments': CommentSchema(many=True).dump(resp).data}
        else:
            return 'success', {'comments': CommentSchema(many=True).dump(post.comments.select()).data}


class PostCommentLastItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        post = get_post(id)

        if not authorized():
            return 'success', {'last_comment': 0}

        last_comment = LastComment.select(lambda p: p.post == post and p.user == pickle.loads(g.user)).get()
        if not last_comment:
            last_comment = LastComment(user=pickle.loads(g.user), post=post, last_id=0)
            db.commit()

        return 'success', {'last_comment': last_comment.last_id}

    @jsend
    @orm.db_session
    def patch(self, id):
        post = get_post(id)

        if not authorized():
            raise Error('E1003')

        args = nparser(g.args, ['comment'])
        if not args.get('comment'):
            return 'success', {}

        if list(post.comments.select(lambda p: p.id == args['comment'])):
            last_comment = LastComment.select(lambda p: p.post == post and p.user == pickle.loads(g.user)).get()
            if last_comment:
                last_comment.last_id = args['comment']
            else:
                last_comment = LastComment(user=pickle.loads(g.user), post=post, last_id=args['comment'])
            db.commit()
            return 'success', {}
        else:
            raise Error('E1074')
