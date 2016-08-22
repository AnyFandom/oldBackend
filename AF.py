from flask import Flask
from flask_restful import Api
import resources
from flask_cors import CORS, cross_origin
from models import *

app = Flask(__name__)

api = Api(app)

api.add_resource(resources.UserItem, '/users/<int:id>')
api.add_resource(resources.UserList, '/users')

@app.before_first_request
def before_first_request():
    db.bind('sqlite', ':memory:')
    db.generate_mapping(create_tables=True)

@app.route('/')
def hello_world():
    return 'Hello World!'

CORS(app)

if __name__ == '__main__':
    app.run(debug=True)
