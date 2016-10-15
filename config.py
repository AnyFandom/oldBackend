import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
ERROR_404_HELP = False

MAX_CONTENT_LENGTH = 10 * 1024 * 1024

SECRET_TOKEN_KEY = '<INSERT YOUR SECRET KEY HERE>'

MIN_MAX = {
    # USER
    'username': [2, 50],
    'password': [6, 200],
    'user_description': [0, 5000],
    # FANDOM
    'fandom_title': [2, 200],
    'fandom_description': [0, 5000],
    # BLOG
    'blog_title': [2, 200],
    'blog_description': [0, 5000],
    # POST
    'post_title': [2, 200],
    'post_content': [2, 150000],
    # COMMENT
    'comment_content': [2, 50000]
}
