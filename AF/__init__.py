import argparse
import json
import pickle
import sys

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_restful import Api
# from flask_marshmallow import Marshmallow
from pony import orm

from flask_socketio import SocketIO, join_room


class MyApi(Api):
    def handle_error(self, e):
        code = getattr(e, 'code', 500)
        if e.__class__.__name__ == 'Error':
            return handle_error(e)
        if code == 405:  # Больше некуда это пихать чтоб работало
            return handle_error(Error('E1202'))
        else:
            return self.make_response({'status': 'error', 'message': json.loads(str(super(MyApi, self).handle_error(e).data, 'utf8'))['message']}, code)

app = Flask(__name__)
api = MyApi(app)
# ma = Marshmallow(app)

socketio = SocketIO(app)

CORS(app)

app.config.from_object('config')
db = orm.Database()

users = {}

# -------------------- #


import AF.socket_utils
from AF.resources.token import Token
from AF.resources.users import UserList, UserItem, UserPostList, UserCommentList
from AF.resources.posts import PostList, PostItem, PostCommentList, PostCommentsNewItem
from AF.resources.comments import CommentList, CommentItem, CommentReadItem
from AF.resources.fandoms import FandomList, FandomItem, FandomBlogList, FandomPostList
from AF.resources.blogs import BlogList, BlogItem, BlogPostList
from AF.utils import jsend

from AF.models import User, Fandom, Blog, Post, Comment
from AF.utils import Error, parser


api.add_resource(Token, '/token')
###
api.add_resource(UserList, '/users')

api.add_resource(UserItem, '/users/current', '/users/id/<int:id>', '/users/profile/<string:username>')
api.add_resource(UserPostList, '/users/current/posts', '/users/id/<int:id>/posts', '/users/profile/<string:username>/posts')
api.add_resource(UserCommentList, '/users/current/comments', '/users/id/<int:id>/comments', '/users/profile/<string:username>/comments')
###
api.add_resource(FandomList, '/fandoms')
api.add_resource(FandomItem, '/fandoms/<int:id>')
api.add_resource(FandomBlogList, '/fandoms/<int:id>/blogs')
api.add_resource(FandomPostList, '/fandoms/<int:id>/posts')
###
api.add_resource(BlogList, '/blogs')
api.add_resource(BlogItem, '/blogs/<int:id>')
api.add_resource(BlogPostList, '/blogs/<int:id>/posts')
###
api.add_resource(PostList, '/posts')
api.add_resource(PostItem, '/posts/<int:id>')
api.add_resource(PostCommentList, '/posts/<int:id>/comments')
api.add_resource(PostCommentsNewItem, '/posts/<int:id>/comments/new')
###
api.add_resource(CommentList, '/comments')
api.add_resource(CommentItem, '/comments/<int:id>')
api.add_resource(CommentReadItem, '/comments/<int:id>/read')

argparser = argparse.ArgumentParser()
argparser.add_argument('-t', '--testing', default='0')
namespace = argparser.parse_args(sys.argv[1:])


def init():
    try:
        db.bind('sqlite', 'database_file.sqlite' if namespace.testing == '0' else ':memory:', create_db=True)
        db.generate_mapping(create_tables=True)
    except TypeError:
        pass
    finally:
        g.ready = True


@app.before_first_request
def before_first_request():
    if not getattr(g, 'ready', False):
        init()


@app.before_request
@orm.db_session
def before_request():
    try:
        g.args = {**request.values.to_dict(), **request.get_json()}
    except TypeError:
        g.args = request.values.to_dict()

    g.args = {**g.args, **request.files}

    args = parser(g.args,
        ('token', str, False))

    if args.get('token', None):
        user = User.check_auth_token(args['token'])
        if not user:
            raise Error('E1001')

        g.user = pickle.dumps(user)


@app.errorhandler(404)
def url_not_found(e):
    # return jsonify({'status': 'error', 'message': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'}), 404
    return handle_error(Error('E1201'))  # Не используем raise потому что он не обрабатывается handle_error автоматически, поэтому вызываем его вручную


# TODO: Надо убрать
# @app.errorhandler(405)
# def method_not_allowed(e):
#     # return jsonify({'status': 'error', 'message': 'The method is not allowed for the requested URL.'}), 405
#     return handle_error(Error('E1202'))


@app.errorhandler(413)
def payload_too_large(e):
    return handle_error(Error('E1203'))


@app.errorhandler(Error)
def handle_error(error):
    return jsonify(error.to_dict()), error.code


@socketio.on('connect')
def socket_connect():
    before_first_request()


@socketio.on('init')
@orm.db_session
def handle_init(token):
    print('NOW')
    if not token:
        if not users.get('guest'):
            users['guest'] = []
        users['guest'].append(request.sid)
        socketio.emit('my response', users)
        return
    user = User.check_auth_token(token)
    if not user:
        return

    if user.id in users.keys():
        users[user.id].append(request.sid)
    else:
        users[user.id] = [request.sid]
    socketio.emit('my response', users)


@socketio.on('disconnect')
def handle_disconnect():
    for i in list(users.keys()):
        if request.sid in users[i]:
            users[i].pop(users[i].index(request.sid))


@socketio.on('join')
def join(room):
    print('join', room)
    join_room(room)


@app.route('/testsockets')
def test_sock():
    AF.socket_utils.hi_everyone()
    return '', 200


@app.route('/env')
@jsend
@orm.db_session
def init_env():
    u = User(username='ADMEN', password_hash=User.hash_password('123454321'))
    f = Fandom(title='Test fandom')
    b = Blog(title='Test blog', fandom=f, owner=u)
    p = Post(title='Test post', content='Lorem ipsum dolor', owner=u, blog=b)
    c = Comment(content='Test comment', depth=0, post=p, owner=u)
    db.commit()
    return 'success', {'status': 'OK'}


@app.route('/clearenv')
def clearenv():
    global db
    if namespace.testing != '0':
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
    return ''
