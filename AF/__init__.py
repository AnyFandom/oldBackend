import argparse
import json
import pickle
import sys

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_restful import Api
from pony import orm

from flask_socketio import SocketIO


class MyApi(Api):
    def handle_error(self, e):
        code = getattr(e, 'code', 500)
        return self.make_response({'status': 'error', 'message': json.loads(str(super(MyApi, self).handle_error(e).data, 'utf8'))['message']}, code)

app = Flask(__name__)
api = MyApi(app)

socketio = SocketIO(app)

CORS(app)

app.config.from_object('config')
db = orm.Database()

users = {}

# -------------------- #


import AF.socket_utils
from AF.resources.token import Token
from AF.resources.users import UserList, UserItem, UserPostList, UserCommentList
from AF.resources.posts import PostList, PostItem, PostCommentList
from AF.resources.comments import CommentList, CommentItem

from AF.models import User
from AF.utils import decode_token, error, parser


api.add_resource(Token, '/token')

api.add_resource(UserList, '/users')
api.add_resource(UserItem, '/users/<string:id>')
api.add_resource(UserPostList, '/users/<string:id>/posts')
api.add_resource(UserCommentList, '/users/<string:id>/comments')

api.add_resource(PostList, '/posts')
api.add_resource(PostItem, '/posts/<int:id>')
api.add_resource(PostCommentList, '/posts/<int:id>/comments')

api.add_resource(CommentList, '/comments')
api.add_resource(CommentItem, '/comments/<int:id>')


@app.before_first_request
def before_first_request():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-t', '--testing', default='0')
    namespace = argparser.parse_args(sys.argv[1:])
    db.bind('sqlite', 'database_file.sqlite' if namespace.testing == '0' else ':memory:', create_db=True)
    db.generate_mapping(create_tables=True)


@app.before_request
@orm.db_session
def before_request():
    try:
        g.args = {**request.values.to_dict(), **request.get_json()}
    except TypeError:
        g.args = request.values.to_dict()

    args = parser(g.args,
        ('token', str, False))

    if args.get('token', None):
        info = decode_token(args['token'])
        if not info:
            return error('E1001', json=True)

        try:
            user = User[info['id']]
        except orm.core.ObjectNotFound:
            return error('E1001', json=True)

        if info['user_salt'] != user.user_salt:
            return error('E1001', json=True)
        g.user = pickle.dumps(user)


@app.errorhandler(404)
def url_not_found(e):
    return jsonify({'status': 'error', 'message': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'status': 'error', 'message': 'The method is not allowed for the requested URL.'}), 405


@socketio.on('connect')
def conn():
    print(request.namespace)


@socketio.on('init')
@orm.db_session
def handle_init(token):
    print('NOW')
    info = decode_token(token)
    if not info:
        print(error('E1001', json=True))

    try:
        user = User[info['id']]
    except orm.core.ObjectNotFound:
        print(error('E1001', json=True))

    if user.id in users.keys():
        users[user.id].append(request.sid)
    else:
        users[user.id] = [request.sid]
    socketio.emit('my response', users)


@app.route('/testsockets')
def test_sock():
    socket_utils.hi_everyone()
    return '', 200
