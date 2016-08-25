from flask_restful import fields

user_marshaller = {
    'id': fields.Integer,
    'username': fields.String,
    'password': fields.String,
    'avatar': fields.String,
    'description': fields.String,
    'user_salt': fields.String
}

# token_marshaller = {
#     'token': fields.String
# }


def jsend(f):
    def wrapper(*args, **kwargs):
        raw = f(*args, **kwargs)  # ("success", {"token": "eyJhbGciOiJIUzI1NiIsIn"}, 201)
        r = {'status': raw[0], 'data' if raw[0] != 'error' else 'message': raw[1]}
        return r, raw[2] if len(raw) > 2 else 200

    return wrapper
