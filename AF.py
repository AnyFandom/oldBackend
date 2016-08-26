from flask import Flask, g
from flask_restful import Api
from flask_cors import CORS, cross_origin

import resources
from utils import *
from models import *
from authentication import *

app = Flask(__name__)
api = Api(app)
CORS(app)

api.add_resource(resources.Token, '/token')

api.add_resource(resources.UserList, '/users')
api.add_resource(resources.UserItem, '/users/<int:id>')


@app.before_first_request
def before_first_request():
    db.bind('sqlite', 'database_file.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)


@app.route('/meme')
@login_required
def meme(*args, **kwargs):
    print(args)
    return 'U r logged in, ' + g.user.username


@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
