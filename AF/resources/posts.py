import pickle

from flask import g, url_for
from flask_restful import Resource, marshal

from pony import orm

from AF import app, db

from AF.utils import authorized, Error, jsend, parser, between
from AF.models import Blog, Post, Comment, LastComment
from AF.marshallers import post_marshaller, comment_marshaller
from AF.socket_utils import send_update


class PostList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized():
            raise Error('E1102')

        args = parser(g.args,
            ('title', str, True),
            ('content', str, True),
            ('preview', str, False),
            ('blog', int, True))
        if not args:
            raise Error('E1101')

        try:
            blog = Blog[args['blog']]
        except orm.core.ObjectNotFound:
            raise Error('E1101')

        title = between(args['title'], app.config['MIN_MAX']['post_title'], 'E1061')
        content = between(args['content'], app.config['MIN_MAX']['post_content'], 'E1062')
        post = Post(title=title, content=content, owner=pickle.loads(g.user), blog=blog, preview_image=args.get('preview', 'https://www.betaseries.com/images/fonds/original/3086_1410380644.jpg'))

        db.commit()
        send_update('post-list')

        return 'success', {'Location': url_for('postitem', id=post.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'posts': marshal(list(Post.select().order_by(Post.id.desc())), post_marshaller)}


class PostItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            return 'success', {'post': marshal(Post[id], post_marshaller)}
        except orm.core.ObjectNotFound:
            raise Error('E1063')

    @jsend
    @orm.db_session
    def delete(self, id):
        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            raise Error('E1063')

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
        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            raise Error('E1063')

        if not authorized():
            raise Error('E1102')

        if post.owner != pickle.loads(g.user):
            raise Error('E1102')

        args = parser(g.args,
            ('title', str, False),
            ('content', str, False),
            ('preview', str, False),)

        if args.get('title'):
            post.title = between(args['title'], app.config['MIN_MAX']['post_title'], 'E1061')
        if args.get('content'):
            post.content = between(args['content'], app.config['MIN_MAX']['post_content'], 'E1062')
        if args.get('preview'):
            post.preview_image = args['preview']

        db.commit()

        return 'success', None, 200


class PostCommentList(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            raise Error('E1063')

        args = parser(g.args,
            ('threaded', int, False))

        if args.get('threaded', None):
            def recursion(comments):
                resp = []
                for comment in comments:
                    resp.append(comment)
                    resp.extend(recursion(comment.answers.order_by(Comment.id)))
                return resp

            resp = Comment.select(lambda p: p.post == post and p.parent is None)  # Получаем все "корневые" комменты
            resp = recursion(resp)  # Рекурсивно формируем список комментов

            return 'success', {'comments': marshal(resp, comment_marshaller)}
        else:
            return 'success', {'comments': marshal(list(Comment.select(lambda p: p.post == post)), comment_marshaller)}


class PostCommentLastItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            raise Error('E1063')

        if not authorized():
            return 'success', {'last_comment': 0}

        last_comment = LastComment.select(lambda p: p.post==post and p.user==pickle.loads(g.user)).get()
        if not last_comment:
            last_comment = LastComment(user=pickle.loads(g.user), post=post, last_id=0)
            db.commit()

        return 'success', {'last_comment': last_comment.last_id}


    @jsend
    @orm.db_session
    def patch(self, id):
        args = parser(g.args,
            ('comment', int, False))
        if not args.get('comment'):
            return 'success', {}
        try:
            post = Post[id]
        except orm.core.ObjectNotFound:
            raise Error('E1063')
        if not authorized():
            raise Error('E1003')
        if args['comment'] in [c.id for c in post.comments]:
            last_comment = LastComment.select(lambda p: p.post==post and p.user==pickle.loads(g.user)).get()
            if last_comment:
                last_comment.last_id = args['comment']
            else:
                last_comment = LastComment(user=pickle.loads(g.user),post=post, last_id=args['comment'])
            db.commit()
            return 'success', {}
        else:
            raise Error('E1074')
