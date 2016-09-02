import pickle
from datetime import datetime

from flask import g, url_for
from flask_restful import Resource, abort, marshal

from pony import orm

from AF import db

from AF.utils import authorized, error, jsend, parser
from AF.models import Post, Comment
from AF.marshallers import post_marshaller, comment_marshaller


class PostList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            return error('E1102')

        args = parser(g.args,
            ('title', str, True),
            ('content', str, True))
        if not args:
            return error('E1101')

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

        args = parser(g.args,
            ('title', str, False),
            ('content', str, False))

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
        args = parser(g.args,
            ('threaded', int, False))

        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            abort(404)

        if args.get('threaded', None):
            def recursion(comments):
                resp = []
                for comment in comments:
                    resp.append(comment)
                    resp.extend(recursion(comment.answers.order_by(Comment.id)))
                return resp

            resp = Comment.select(lambda p: p.post == post and p.parent is None)[:]  # Получаем все "корневые" комменты
            resp = recursion(resp)  # Рекурсивно формируем список комментов

            return 'success', {'comments': marshal(resp, comment_marshaller)}
        else:
            return 'success', {'comments': marshal(list(Comment.select(lambda p: p.post == post)[:]), comment_marshaller)}