from flask import g, url_for
from flask_restful import Resource, abort, marshal

from pony import orm

from AF import db

from AF.utils import authorized, error, jsend, parser
from AF.models import User, Staff, Fandom, Blog
from AF.marshallers import staff_marshaller


class StaffList(Resource):
    @jsend
    @orm.db_session
    def post(self):
        if not authorized(11):  # GAdmin
            return error('E1102')

        args = parser(g.args,
            ('user', int, True),
            ('type', int, True),
            ('role', int, True),
            ('fadnom', int, False),
            ('blog', int, False))
        if not args:
            return error('E1101')

        try:
            user = User[args['user']]
        except orm.core.ObjectNotFound:
            return error('E1101')

        if args['role'] not in [1, 2]:
            return error('E1101')

        staff = Staff(user=user, type=args['type'], role=args['role'])

        if args['type'] == 1:  # If we are adding GAdmin/GModer
            pass
        if args['type'] == 2 and args.get('fandom', None) is not None:  # If we are adding FAdmin/FModer
            try:
                staff.fandom = Fandom[args['fandom']]
            except orm.core.ObjectNotFound:
                return error('E1101')
        elif args['type'] == 3 and args.get('blog', None) is not None:  # If we are adding BAdmin/BModer
            try:
                staff.blog = Blog[args['blog']]
            except orm.core.ObjectNotFound:
                return error('E1101')
        else:
            return error('E1101')

        db.commit()

        return 'success', {'Location': url_for('staffitem', id=staff.id)}, 201

    @jsend
    @orm.db_session
    def get(self):
        return 'success', {'staff': marshal(list(Staff.select()), staff_marshaller)}


class StaffItem(Resource):
    @jsend
    @orm.db_session
    def get(self, id):
        try:
            return 'success', {'staff': marshal(Staff[id], staff_marshaller)}
        except orm.core.ObjectNotFound:
            abort(404)

    @jsend
    @orm.db_session
    def delete(self, id):  # TODO: Сделать так чтоб каждый крестьянин смог удалять ГАдминов по желанию левой пятки
        try:
            staff = Staff[id]
        except orm.core.ObjectNotFound:
            abort(404)

        if not authorized(11):  # GAdmin
            return error('E1102')

        staff.delete()
        db.commit()

        return 'success', None
