from flask_restful import Resource, marshal_with
from flask_restful.reqparse import RequestParser
from models import *
from utils import *
from flask import make_response, url_for

class UserKeyList(Resource):
    @orm.db_session
    def get(self):
        return 

class UserItem(Resource):
    @orm.db_session
    @marshal_with(user_marshaller)
    def get(self, id):
        return User[id]


class UserList(Resource):
    @orm.db_session
    @marshal_with(user_marshaller)
    def post(self):
        parser = RequestParser()
        parser.add_argument('login', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('avatar', type=str, required=False)
        parser.add_argument('description', type=str, required=False)
        args = parser.parse_args()
        u = User(login=args.login, password=args.password)
        if args.get('avatar', None):
            u.avatar = args['avatar']
        if args.get('description', None):
            u.description = args['description']
        db.commit()
        resp = make_response('', 201)
        resp.headers['Location'] = url_for('useritem', id=u.id)
        return resp

    @orm.db_session
    @marshal_with(user_marshaller)
    def get(self):
        return list(User.select()[:])