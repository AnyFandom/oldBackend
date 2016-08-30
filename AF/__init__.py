import argparse
import json
import pickle
import sys

from flask import Flask, g, jsonify
from flask_cors import CORS
from flask_restful import Api
from flask_restful.reqparse import RequestParser
from pony import orm


class MyApi(Api):
    def handle_error(self, e):
        code = getattr(e, 'code', 500)
        return self.make_response({'status': 'error', 'message': json.loads(str(super(MyApi, self).handle_error(e).data, 'utf8'))['message']}, code)

app = Flask(__name__)
api = MyApi(app)

CORS(app)

app.config.from_object('config')
db = orm.Database()


# -------------------- #


from AF.resources.token import Token
from AF.resources.users import UserList, UserItem, UserPostList, UserCommentList
from AF.resources.posts import PostList, PostItem, PostCommentList
from AF.resources.comments import CommentList, CommentItem

from AF.models import User
from AF.utils import decode_token, error


api.add_resource(Token, '/token')

api.add_resource(UserList, '/users')
api.add_resource(UserItem, '/users/<int:id>')
api.add_resource(UserPostList, '/users/<int:id>/posts')
api.add_resource(UserCommentList, '/users/<int:id>/comments')

api.add_resource(PostList, '/posts')
api.add_resource(PostItem, '/posts/<int:id>')
api.add_resource(PostCommentList, '/posts/<int:id>/comments')

api.add_resource(CommentList, '/comments')
api.add_resource(CommentItem, '/comments/<int:id>')


@app.before_first_request
def before_first_request():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--testing', default='0')
    namespace = parser.parse_args(sys.argv[1:])
    db.bind('sqlite', 'database_file.sqlite' if namespace.testing == '0' else ':memory:', create_db=True)
    db.generate_mapping(create_tables=True)


@app.before_request
@orm.db_session
def before_request():
    parser = RequestParser()
    parser.add_argument('token', type=str, required=False)
    args = parser.parse_args()
    if args.get('token', None):
        info = decode_token(args['token'])
        if not info:
            return error('E1001', json=True)
        user = User[info['id']]
        if not user:
            return error('E1001', json=True)
        if info['user_salt'] != user.user_salt:
            return error('E1001', json=True)
        g.user = pickle.dumps(user)


@app.errorhandler(404)
def url_not_found(e):
    return jsonify({'status': 'error', 'message': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'status': 'fail', 'message': 'The method is not allowed for the requested URL.'}), 405
