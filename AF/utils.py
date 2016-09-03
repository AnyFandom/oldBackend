import pickle

import jwt
from flask import g, jsonify

from AF.models import Super


def jsend(f):
    def wrapper(*args, **kwargs):
        raw = f(*args, **kwargs)  # ("success", {"token": "eyJhbGciOiJIUzI1NiIsIn"}, 201)
        if not raw:
            return None
        r = {'status': raw[0], 'data' if raw[0] != 'error' else 'message': raw[1]}
        return r, raw[2] if len(raw) > 2 else 200
    return wrapper


def parser(dictionary, *args):  # (name, type, required)
    resp = {}
    for arg in args:
        item = dictionary.get(arg[0])
        if arg[1] == int and isnum(item) is True:  # if argument should be int and it is, but in string
            resp[arg[0]] = int(dictionary[arg[0]])
        elif arg[2] and (item is None or not isinstance(item, arg[1])):  # if required and (no such item or item is wrong type)
            return None
        elif not arg[2] and (item is None or not isinstance(item, arg[1])):  # if not required and (no such item or item is wrong type)
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


def error(code, json=False):
    errors = {
        # AUTH
        'E1001': ['Token is invalid.', 403],
        'E1002': ['Incorrect username or password.', 403],
        'E1003': ['You need to enter the token to access this page', 403],
        # POSTS
        'E1011': ['You are not the author of this post.', 403],
        # COMMENTS
        'E1021': ['You are not the author of the comment', 403],
        # OTHER
        'E1101': ['One or multiple required parameters were not transferred or invalid.', 400],
        'E1102': ['You don\'t have sufficent permissions to access this page.', 403]
    }
    if not json:
        return 'fail', {'code': code, 'message': errors[code][0]}, errors[code][1]
    else:
        return jsonify({'status': 'fail', 'data': {'code': code, 'message': errors[code][0]}}), errors[code][1]


def generate_token(id, user_salt):
    return jwt.encode({'id': id, 'user_salt': user_salt}, 'VERY SECRET KEY', algorithm='HS256')


def decode_token(token):
    try:
        return jwt.decode(token, 'VERY SECRET KEY', algorithm='HS256')
    except:
        return None


def authorized(blog=None, fandom=None, owner=None, *args):
    try:
        user = pickle.loads(g.user)
    except KeyError:
        return []

    resp = []

    if user == owner:
        resp.append('owner')

    for arg in args:
        if arg == 'user':
            resp.append('user')

        elif arg == 'sadmin' or arg == 'smoder':
            super = get_first(Super.select(lambda p: p.user == user)[:])
            if super is not None:
                if arg == 'sadmin' and super.role == 0:
                    resp.append('sadmin')
                if arg == 'smoder' and super.role == 1:
                    resp.append('smoder')

        elif arg == 'fadmin' or arg == 'fmoder':
            if arg == 'fadmin' and user in fandom.admins:
                resp.append('fadmin')
            if arg == 'fmoder' and user in fandom.admins:
                resp.append('fmoder')

        elif arg == 'badmin' or arg == 'bmoder':
            if arg == 'badmin' and user in blog.admins:
                resp.append('badmin')
            if arg == 'bmoder' and user in blog.moders:
                resp.append('bmoder')

    # for key in kwargs:
    #     if key == 'owner':
    #         owner = kwargs[key]
    #         if user == owner:
    #             resp.append('owner')
    #     elif key == 'fadmin' or key == 'fmoder':
    #         fandom = kwargs[key]
    #         if key == 'fadmin' and user in fandom.admins:
    #             resp.append('fadmin')
    #         if key == 'fmoder' and user in fandom.moders:
    #             resp.append('fmoders')
    #
    #     elif key == 'badmin' or key == 'bmoder':
    #         blog = kwargs[key]
    #         if key == 'badmin' and user in blog.admins:
    #             resp.append('badmin')
    #         if key == 'bmoder' and user in blog.moders:
    #             resp.append('bmoder')

    return resp


def get_first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default
