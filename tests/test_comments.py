import pytest
import requests
from conf import BASE_URL

token = ''
user_location = ''
username = 'unittest-comments'
user = {}

fandom = {}
fandom_location = ''

blog = {}
blog_location = ''

post = {}
post_location = ''

comment = {}
comment_location = ''

answer = {}
answer_location = ''

last_comment = None


def setup_module(module):
    requests.get(BASE_URL+'/clearenv')


def teardown_module(module):
    requests.get(BASE_URL+'/clearenv')


class TestComments():
    def user_add(self):
        global user_location
        options = {
            'username': '{}'.format(username),
            'password': '{}'.format(username),
        }

        r = requests.post(BASE_URL+'/users', data=options)
        data = r.json()
        print(data)
        assert r.status_code == 201
        assert 'Location' in list(data['data'].keys())
        user_location = data['data']['Location']


    def user_authenficate(self):
        global token
        options = {
            'username': '{}'.format(username),
            'password': '{}'.format(username),
        }
        r = requests.post(BASE_URL+'/token', data=options)
        data = r.json()['data']
        token = data['token']
        assert 'token' in list(data.keys())


    def user_get_user_by_user_location(self):
        global user
        options = {
        }
        r = requests.get(BASE_URL+user_location, data=options)
        data = r.json()['data']
        assert r.status_code == 200
        assert 'user' in data
        user = data['user']


    def fandom_add(self):
        global fandom_location
        options = {
            'token': token,
            'title': 'Unittest fandom title',
            'description': 'Unittest fandom description',
            'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
        }
        r = requests.post(BASE_URL+'/fandoms', data=options)
        data = r.json()['data']
        assert r.status_code == 201
        assert 'Location' in list(data.keys())
        fandom_location = data['Location']


    def fandom_get_by_location(self):
        global fandom
        options = {
        }
        r = requests.get(BASE_URL+fandom_location, params=options)
        data = r.json()['data']
        assert r.status_code == 200
        assert 'fandom' in list(data.keys())
        fandom = data['fandom']


    def blog_add(self):
        global blog_location
        options = {
            'token': token,
            'fandom': fandom['id'],
            'title': 'Test',
            'description': 'Test',
        }
        r = requests.post(BASE_URL+'/blogs', data=options)
        data = r.json()['data']
        assert r.status_code == 201
        assert 'Location' in list(data.keys())
        blog_location = data['Location']


    def blog_get_by_location(self):
        global blog
        options = {
        }
        r = requests.get(BASE_URL+blog_location)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'blog' in list(data.keys())
        blog = data['blog']


    def post_add(self):
        global post_location
        options = {
            'token': token,
            'title': 'Test',
            'blog': blog['id'],
            'content': 'Test content',
            'preview': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code == 201
        data = r.json()['data']
        assert 'Location' in list(data.keys())
        post_location = data['Location']


    def post_get_by_location(self):
        global post
        options = {
        }
        r = requests.get(BASE_URL+post_location, params=options)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'post' in data
        post = data['post']


    def test_init(self):
        self.user_add()
        self.user_authenficate()
        self.user_get_user_by_user_location()
        self.fandom_add()
        self.fandom_get_by_location()
        self.blog_add()
        self.blog_get_by_location()
        self.post_add()
        self.post_get_by_location()


    #
    # Test comment add
    #


    def test_comment_add_without_token(self):
        options = {
            'post': post['id'],
            'content': 'Test comment',
            'parent': 0,
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code > 201


    def test_comment_add_without_parent(self):
        options = {
            'token': token,
            'post': post['id'],
            'content': 'Test comment',
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code == 201


    def test_comment_add_with_wrong_parent(self):
        options = {
            'token': token,
            'post': post['id'],
            'content': 'Test comment',
            'parent': 10,
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code > 201


    def test_comment_add_without_post(self):
        options = {
            'token': token,
            'content': 'Test comment',
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code > 201


    def test_comment_add_with_wrong_post(self):
        options = {
            'token': token,
            'content': 'Test comment',
            'post': 100500
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code > 201


    def test_comment_add_without_content(self):
        options = {
            'token': token,
            'post': post['id']
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code > 201


    def test_comment_add_with_short_content(self):
        options = {
            'token': token,
            'content': 'T',
            'post': post['id']
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code > 201


    def test_comment_add_with_long_content(self):
        options = {
            'token': token,
            'content': 'T'*50001,
            'post': post['id']
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code > 201


    def test_comment_add_with_parent_zero(self):
        global comment_location
        options = {
            'token': token,
            'post': post['id'],
            'content': 'Test comment',
            'parent': 0,
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code == 201
        data = r.json()['data']
        assert 'Location' in data
        comment_location = data['Location']


    def test_comment_add_with_parent_comment(self):
        global answer_location
        options = {
            'token': token,
            'post': post['id'],
            'content': 'Test comment',
            'parent': 1,
        }
        r = requests.post(BASE_URL+'/comments', data=options)
        assert r.status_code == 201
        data = r.json()['data']
        assert 'Location' in data
        answer_location = data['Location']



    #
    # Test get comment
    #


    def test_comment_get_by_location(self):
        global comment
        options = {
        }
        r = requests.get(BASE_URL+comment_location, params=options)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'comment' in data
        comment = data['comment']


    def test_comment_get_by_id(self):
        options = {
        }
        r = requests.get(BASE_URL+'/comments/{}'.format(comment['id']), params=options)
        r.status_code == 200

    def test_comment_get_from_list(self):
        options = {
        }
        r = requests.get(BASE_URL+'/comments', params=options)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'comments' in data
        comments = [c['id'] for c in data['comments']]
        assert comment['id'] in comments


    def test_comment_get_from_post(self):
        options = {
        }
        r = requests.get(BASE_URL+'/posts/{}/comments'.format(post['id']), params=options)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'comments' in data
        comments = [c['id'] for c in data['comments']]
        assert comment['id'] in comments


    #
    # Test comment edit
    #


    def test_comment_edit_without_token(self):
        options = {
        }
        r = requests.patch(BASE_URL+'/comments/{}'.format(comment['id']), data=options)
        assert r.status_code > 200


    def test_comment_edit_with_token(self):
        options = {
            'token': token,
        }
        r = requests.patch(BASE_URL+'/comments/{}'.format(comment['id']), data=options)
        assert r.status_code == 200


    def test_comment_edit_short_content(self):
        options = {
            'token': token,
            'content': 'T'
        }
        r = requests.patch(BASE_URL+'/comments/{}'.format(comment['id']), data=options)
        assert r.status_code > 200


    def test_comment_edit_long_content(self):
        options = {
            'token': token,
            'content': 'T'*50001
        }
        r = requests.patch(BASE_URL+'/comments/{}'.format(comment['id']), data=options)
        assert r.status_code > 200


    def test_comment_edit(self):
        options = {
            'token': token,
            'content': 'Test edit'
        }
        edit_r = requests.patch(BASE_URL+'/comments/{}'.format(comment['id']), data=options)
        assert edit_r.status_code == 200
        assert comment['content'] != options['content']
        self.test_comment_get_by_location()
        assert comment['content'] == options['content']


    #
    # Test last_comment
    #


    def test_lastComment_get_without_token(self):
        options = {
        }
        r = requests.get(BASE_URL+'/posts/{}/comments/last'.format(post['id']), params=options)
        assert r.status_code == 200
        data = r.json()['data']
        print(data)
        assert 'last_comment' in data


    def test_lastComment_get(self):
        global last_comment
        options = {
            'token': token,
        }
        r = requests.get(BASE_URL+'/posts/{}/comments/last'.format(post['id']), params=options)
        assert r.status_code == 200
        data = r.json()['data']
        print(data)
        assert 'last_comment' in data
        last_comment = data['last_comment']


    def test_lastComment_set_without_token(self):
        options = {
            'comment': comment['id'],
        }
        r = requests.patch(BASE_URL+'/posts/{}/comments/last'.format(post['id']), data=options)
        assert r.status_code > 200


    def test_lastComment_set_without_comment(self):
        options = {
            'token': token,
        }
        r = requests.patch(BASE_URL+'/posts/{}/comments/last'.format(post['id']), data=options)
        assert r.status_code == 200


    def test_lastComment_set(self):
        options = {
            'token': token,
            'comment': comment['id']
        }
        r = requests.patch(BASE_URL+'/posts/{}/comments/last'.format(post['id']), data=options)
        assert r.status_code == 200
        assert last_comment < options['comment']
        self.test_lastComment_get()
        assert last_comment == options['comment']



    #
    # Test comment delete
    #


    def test_comment_delete_without_token(self):
        options = {
        }
        r = requests.delete(BASE_URL+'/comments/{}'.format(comment['id']), data=options)
        assert r.status_code > 200


    def test_comment_delete(self):
        options = {
            'token': token,
        }
        r = requests.delete(BASE_URL+'/comments/{}'.format(comment['id']), data=options)
        assert r.status_code == 200

    def test_comment_not_deleted_with_answers(self):
        options = {
        }
        r = requests.get(BASE_URL+answer_location, params=options)
        assert r.status_code == 200
