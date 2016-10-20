import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
ERROR_404_HELP = False

MAX_CONTENT_LENGTH = 10 * 1024 * 1024

SECRET_TOKEN_KEY = '<INSERT YOUR SECRET KEY HERE>'

MIN_MAX = {
    # USER
    'username': {'min': 2, 'max': 50},
    'password': {'min': 6, 'max': 200},
    'user_description': {'min': 0, 'max': 5000},
    # FANDOM
    'fandom_title': {'min': 2, 'max': 200},
    'fandom_description': {'min': 0, 'max': 5000},
    # BLOG
    'blog_title': {'min': 2, 'max': 200},
    'blog_description': {'min': 0, 'max': 5000},
    # POST
    'post_title': {'min': 2, 'max': 200},
    'post_content': {'min': 2, 'max': 150000},
    # COMMENT
    'comment_content': {'min': 2, 'max': 50000}
}
