# utils.py

from flask import g

from AF import app


class Error(Exception):
    errors = {
        # AUTH
        'E1001': ['Token is invalid.', 403],
        'E1002': ['Incorrect username or password.', 403],
        'E1003': ['You need to enter the token to access this page', 403],
        # POSTS
        'E1011': ['You are not the author of this post.', 403],
        # COMMENTS
        'E1021': ['You are not the author of the comment.', 403],
        # USERS
        'E1031': ['Username must be unique.', 400],
        'E1032': ['Username must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['username']), 400],
        'E1033': ['Password must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['password']), 400],
        'E1034': ['User description must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['user_description']), 400],
        # FANDOMS
        'E1041': ['Fandom title must be unique.', 400],
        'E1042': ['Fandom title must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['fandom_title']), 400],
        'E1043': ['Fandom description must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['fandom_description']), 400],
        # BLOGS
        'E1051': ['Blog title must be unique in this fandom', 400],
        'E1052': ['Blog title must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['blog_title']), 400],
        'E1053': ['Blog description must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['blog_description']), 400],
        # POSTS
        'E1061': ['Post title must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['post_title']), 400],
        'E1062': ['Post content must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['post_content']), 400],
        # COMMENTS
        'E1071': ['Reserved', 400],  # Анти-спам
        'E1072': ['Comment content must be more than {} and less than {} symbols.'.format(*app.config['MIN_MAX']['comment_content']), 400],
        # OTHER
        'E1101': ['One or multiple required parameters were not transferred or invalid.', 400],
        'E1102': ['You don\'t have sufficent permissions to access this page.', 403]
    }

    def __init__(self, error_code):
        Exception.__init__(self)
        self.data = {'code': error_code, 'message': self.errors[error_code][0]}
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


def isnum(arg):
    try:
        resp = arg.isnumeric()
    except AttributeError:
        resp = False
    return resp


def authorized():
    return True if g.get('user', None) else False


def between(x, y, e):
    # return y[0] < len(x) < y[1]
    if y[0] < len(x) < y[1]:
        return x
    else:
        raise Error(e)
