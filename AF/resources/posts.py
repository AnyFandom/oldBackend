import pickle

from flask import g, url_for
from flask_restful import Resource

from pony import orm

from AF import db

from AF.utils import authorized, Error, jsend, nparser, get_comments_new
from AF.models import Post, Comment, LastComment, ReadComments
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


class PostCommentsNewItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        post = get_post(id)

        if not authorized():
            return 'success', {'comments': CommentSchema(many=True).dump(list(post.comments)).data}


        last_comment = LastComment.select(lambda lc: lc.post==post and lc.user==pickle.loads(g.user)).get()

        if last_comment:
            last_comment_id = last_comment.comment.id
        else:
            last_comment_id = 0

        comments_new = get_comments_new(pickle.loads(g.user), post, last_comment_id)

        return 'success', {'comments': CommentSchema(many=True).dump(comments_new).data}

    @jsend
    @orm.db_session
    def post(self, id):
        post = get_post(id)

        if not authorized():
            return 'success', {'comments': CommentSchema(many=True).dump(list(post.comments)).data}

        user = pickle.loads(g.user)

        last_comment = LastComment.select(lambda lc: lc.post==post and lc.user==user).get()

        post_comments = list(post.comments)
        post_comments.sort(key=lambda c: c.id)

        if last_comment:
            last_comment.comment = post_comments[-1]
        else:
            last_comment = LastComment(post=post, user=user, comment=post_comments[-1])

        print(last_comment.comment)

        orm.delete(rc for rc in ReadComments if rc.post==post and rc.user==user)

        db.commit()

        return 'success', None, 200
