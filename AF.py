# AF.py

import json

from flask import Flask, g, jsonify
from flask_restful import Api, abort
from flask_cors import CORS, cross_origin
import argparse, sys
import resources
from utils import *
from models import *
from authentication import *


app = Flask(__name__)


class MyApi(Api):
    def handle_error(self, e):
        code = getattr(e, 'code', 500)
        return self.make_response( {'status': 'error', 'message': json.loads(str(super(MyApi, self).handle_error(e).data, 'utf8'))['message']}, code )

api = MyApi(app)

CORS(app)


@app.errorhandler(404)
@jsend
def url_not_found(e):
    return 'fail', {'message': 'The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.'}, 404


@app.errorhandler(405)
def method_not_allowed(e):
    return 'fail', {'message': 'The method is not allowed for the requested URL.'}, 405

api.add_resource(resources.Test, '/test')

api.add_resource(resources.Token, '/token')

api.add_resource(resources.UserList, '/users')
api.add_resource(resources.UserItem, '/users/<int:id>')

api.add_resource(resources.PostList, '/posts')
api.add_resource(resources.PostItem, '/posts/<int:id>')


@api.representation('application/json')
def fix_json_output(data, code, headers=None):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


@app.before_first_request
def before_first_request():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--testing', default='0')
    namespace = parser.parse_args(sys.argv[1:])
    db.bind('sqlite', 'database_file.sqlite' if namespace.testing == '0' else ':memory:', create_db=True)
    db.generate_mapping(create_tables=True)


@app.before_request
@jsend
@orm.db_session
def before_request():
    parser = RequestParser()
    parser.add_argument('token', type=str, required=False)
    args = parser.parse_args()
    if args.get('token', None):
        info = decode_token(args['token'])
        if not info:
            return 'fail', {'message': 'Authorization failed: token is invalid'}, 403
        u = User.select(lambda p: p.id == info['id'])[:]
        if info['user_salt'] != u[0].user_salt:
            return 'fail', {'message': 'Authorization failed: token is invalid'}, 403
        g.user = u[0]


# say no to that shiet
# @app.route('/meme')
# @jsend
# # @login_required
# def meme(*args, **kwargs):
#     if not authorization():
#         return 'fail', {'message': 'You dont have sufficent permissions to access this page'}, 403
#     return 'success', {'message': 'U r logged in, ' + g.user.username}
#
#
# @app.route('/')
# def hello_world():
#     return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
