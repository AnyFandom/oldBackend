# utils.py

from flask import g


class Error(Exception):
    errors = {
        # AUTH
        'E1001': ['Specified authentication token is invalid.', 403],
        'E1002': ['Incorrect username or password.', 403],
        'E1003': ['You need to enter the authentication token to access this page', 403],
        'E1004': ['Old password isn\'t valid.', 403],
        # POSTS
        'E1011': ['You are not the author of this post.', 403],
        # COMMENTS
        'E1021': ['You are not the author of the comment.', 403],
        # USERS
        'E1031': ['Username must be unique.', 409],
        'E1035': ['User with specified ID or username doesn\'t exists.', 404],
        'E1036': ['To change password you need to enter the old one in the "password_old" field.', 403],
        # FANDOMS
        'E1041': ['Fandom title must be unique.', 409],
        'E1045': ['Fandom with specified ID doesn\'t exists.', 404],
        # BLOGS
        'E1051': ['Blog title must be unique in this fandom', 409],
        'E1055': ['Blog with specified ID doesn\'t exists.', 404],
        # POSTS
        'E1065': ['Post with specified ID doesn\'t exists.', 404],
        # COMMENTS
        'E1071': ['Reserved', 400],  # Анти-спам
        'E1074': ['Comment does not exist or does not belong to this post', 403],
        'E1075': ['Comment with specified ID doesn\'t exists.', 404],
        # OTHER
        'E1101': ['One or multiple required parameters were not transferred or invalid. See "details" for details.', 400],
        'E1102': ['You don\'t have sufficent permissions to execute this operation.', 403],
        'E1201': ['The specified resource doesn\'t exists.', 404],
        'E1202': ['The resource doesn\'t support the specified HTTP method.', 405],
        'E1203': ['The size of the request body exceeds the maximum size permitted.', 413]
    }

    def __init__(self, error_code, details=None):
        Exception.__init__(self)
        self.data = {'code': error_code, 'message': self.errors[error_code][0]}
        if details:
            self.data['details'] = details
        self.code = self.errors[error_code][1]

    def to_dict(self):
        return {'status': 'fail', 'data': self.data}


def jsend(f):
    def wrapper(*args, **kwargs):
        raw = f(*args, **kwargs)  # ("success", {"token": "eyJhbGciOiJIUzI1NiIsIn"}, 201)
        if not raw:
            return None
        r = {'status': raw[0], 'data' if raw[0] != 'error' else 'message': raw[1]}
        return r, raw[2] if len(raw) > 2 else 200
    return wrapper


def xstr(s):
    return '' if s is None else str(s)


def parser(dictionary, *args):  # (name, type, required)
    resp = {}
    for arg in args:
        item = dictionary.get(arg[0])
        if arg[1] == int and isnum(item) is True:  # if argument should be int and it is, but in string
            resp[arg[0]] = int(item)
        elif arg[2] and (not len(xstr(item)) or not isinstance(item, arg[1])):  # if required and (no such item or item is wrong type)
            return None
        elif not arg[2] and (not len(xstr(item)) or not isinstance(item, arg[1])):  # if not required and (no such item or item is wrong type)
            continue
        else:
            resp[arg[0]] = dictionary[arg[0]]
    return resp


def nparser(dictionary, args):
    keys = dictionary.keys() & args
    return {key: dictionary[key] for key in keys}


def isnum(arg):
    try:
        resp = arg.isnumeric()
    except AttributeError:
        resp = False
    return resp


def authorized():
    return True if g.get('user', None) else False
