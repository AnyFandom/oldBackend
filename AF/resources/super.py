from flask import g, url_for
from flask_restful import Resource, abort, marshal

from pony import orm

from AF import db

from AF.utils import authorized, error, jsend, parser
from AF.models import Super, User
from AF.marshallers import super_marshaller


class AdminList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized('sadmin'):
            return error('E1102')

        args = parser(g.args,
            ('user', int, True))
        if not args:
            return error('E1101')

        try:
            user = User[args['user']]
        except orm.core.ObjectNotFound:
            return error('E1101')

        superadmin = Super(user=user, role=0)
        db.commit()

        return 'success', None

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'superadmins': marshal(list(Super.select(lambda p: p.role == 0)[:]), super_marshaller)}


class ModerList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized('sadmin'):
            return error('E1102')

        args = parser(g.args,
            ('user', int, True))
        if not args:
            return error('E1101')

        try:
            user = User[args['user']]
        except orm.core.ObjectNotFound:
            return error('E1101')

        supermoder = Super(user=user, role=1)
        db.commit()

        return 'success', None

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'supermoders': marshal(list(Super.select(lambda p: p.role == 1)[:]), super_marshaller)}
