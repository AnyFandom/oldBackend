from flask_restful import fields

user_marshaller = {
    'login': fields.String,
    'password': fields.String,
    'avatar': fields.String,
    'description': fields.String,
}