import pickle

import jwt
from flask import g, jsonify


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
        # FANDOMS
        'E1031': ['User is already admin of this fandom', 403],
        'E1032': ['User is already moder of this fandom', 403],
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


def authorized(*args, blog=None, fandom=None, owner=None):
    # 0 - user
    # 11 - GlobalAdmin, 12 - GlobalModer
    # 20 - FandomOwner, 21 - FandomAdmin, 22 - FandomModer
    # 30 - BlogOwner, 31 - BlogAdmin, 32 - BlogModer
    try:
        user = pickle.loads(g.user)
    except AttributeError:
        return []

    resp = []

    if user == owner:  # Comment/Post owner, NOT Blog owner
        resp.append('owner')

    rights = list(user.rights)

    for arg in args:
        print(arg)
        if arg == 0:
            resp.append('user')
        else:

            for right in rights:
                if arg in [11, 12] and right.type == 1:
                    if arg == 11 and right.role == 1:
                        resp.append('gadmin')
                    elif arg == 12 and right.role == 2:
                        resp.append('gmoder')

                elif arg in [20, 21, 22] and right.type == 2 and right.fandom == fandom:
                    if arg == 21 and right.role == 1:
                        resp.append('fadmin')
                    elif arg == 22 and right.role == 2:
                        resp.append('fmoder')

                elif arg in [30, 31, 32] and right.type == 2 and right.blog == blog:
                    if arg == 30 and blog.owner == user:
                        resp.append('bowner')
                    elif arg == 31 and right.role == 1:
                        resp.append('badmin')
                    elif arg == 32 and right.role == 2:
                        resp.append('bmoder')

        # elif arg == 20 or arg == 21 or arg == 22:
        #     if arg == 20 and user == fandom.owner:
        #         resp.append('fowner')
        #     if arg == 21 and user in fandom.admins:
        #         resp.append('fadmin')
        #     if arg == 22 and user in fandom.admins:
        #         resp.append('fmoder')
        #
        # elif arg == 30 or arg == 31 or arg == 32:
        #     if arg == 30 and user in blog.admins:
        #         resp.append('bowner')
        #     if arg == 31 and user in blog.moders:
        #         resp.append('badmin')
        #     if arg == 32 and user == blog.owner:
        #         resp.append('bmoder')

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
