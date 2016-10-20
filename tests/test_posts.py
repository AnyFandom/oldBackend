import pytest
import requests
from conf import BASE_URL

token = ''
user_location = ''
username = 'unittest-posts'
user = {}

fandom = {}
fandom_location = ''

blog = {}
blog_location = ''

post = {}
post_location = ''


def setup_module(module):
    requests.get(BASE_URL+'/clearenv')


def teardown_module(module):
    requests.get(BASE_URL+'/clearenv')


class TestPosts():
    #
    # Add, authenficate and get user.
    #


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


    def test_init(self):
        self.user_add()
        self.user_authenficate()
        self.user_get_user_by_user_location()
        self.fandom_add()
        self.fandom_get_by_location()
        self.blog_add()
        self.blog_get_by_location()


    #
    # Test post add
    #


    def test_post_add_without_token(self):
        options = {
            'title': 'Test',
            'blog': blog['id'],
            'content': 'Test content',
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code > 201


    def test_post_add_without_title(self):
        options = {
            'token': token,
            'blog': blog['id'],
            'content': 'Test content',
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code > 201


    def test_post_add_with_short_title(self):
        global post_location
        options = {
            'token': token,
            'title': 'T',
            'blog': blog['id'],
            'content': 'Test content',
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code > 201


    def test_post_add_with_long_title(self):
        global post_location
        options = {
            'token': token,
            'title': 'T'*201,
            'blog': blog['id'],
            'content': 'Test content',
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code > 201


    def test_post_add_without_content(self):
        options = {
            'token': token,
            'title': 'Test',
            'blog': blog['id'],
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code > 201


    def test_post_add_with_short_content(self):
        global post_location
        options = {
            'token': token,
            'title': 'Test',
            'blog': blog['id'],
            'content': 'T',
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code > 201


    def test_post_add_with_long_content(self):
        global post_location
        options = {
            'token': token,
            'title': 'Test',
            'blog': blog['id'],
            'content': 'T'*150001,
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code > 201


    def test_post_add_without_blog(self):
        options = {
            'token': token,
            'title': 'Test',
            'content': 'Test content',
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code > 201


    def test_post_add_with_wrong_blog(self):
        options = {
            'token': token,
            'title': 'Test',
            'blog': 100500,
            'content': 'Test content',
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code > 201


    def test_post_add_with_token(self):
        global post_location
        options = {
            'token': token,
            'title': 'Test',
            'blog': blog['id'],
            'content': 'Test content',
            'preview_image': 'http://cs4.pikabu.ru/images/big_size_comm/2014-03_5/13954947452308.png'
        }
        r = requests.post(BASE_URL+'/posts', data=options)
        assert r.status_code == 201
        data = r.json()['data']
        assert 'Location' in list(data.keys())
        post_location = data['Location']


    #
    # Test get blog
    #

    def test_post_get_by_location(self):
        global post
        options = {
        }
        r = requests.get(BASE_URL+post_location, params=options)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'post' in data
        post = data['post']


    def test_post_get_by_id(self):
        options = {
        }
        r = requests.get(BASE_URL+'/posts/{}'.format(post['id']), params=options)
        assert r.status_code == 200


    def test_post_get_from_fandom(self):
        options = {
        }
        r = requests.get(BASE_URL+'/fandoms/{}/posts'.format(fandom['id']), params=options)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'posts' in data
        fandom_posts = [p['id'] for p in data['posts']]
        assert post['id'] in fandom_posts


    def test_post_get_from_blog(self):
        options = {
        }
        r = requests.get(BASE_URL+'/blogs/{}/posts'.format(blog['id']), params=options)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'posts' in data
        blog_posts = [p['id'] for p in data['posts']]
        assert post['id'] in blog_posts


    #
    # Test edit post
    #

    def test_post_edit_without_token(self):
        options = {
        }
        r = requests.patch(BASE_URL+'/posts/{}'.format(post['id']), data=options)
        assert r.status_code != 200


    def test_post_edit_with_token(self):
        options = {
            'token': token,
        }
        r = requests.patch(BASE_URL+'/posts/{}'.format(post['id']), data=options)
        assert r.status_code == 200


    def test_post_edit_short_title(self):
        options = {
            'token': token,
            'title': 'T',
        }
        r = requests.patch(BASE_URL+'/posts/{}'.format(post['id']), data=options)
        assert r.status_code > 200


    def test_post_edit_long_title(self):
        options = {
            'token': token,
            'title': 'T'*201,
        }
        r = requests.patch(BASE_URL+'/posts/{}'.format(post['id']), data=options)
        assert r.status_code > 200


    def test_post_edit_short_content(self):
        options = {
            'token': token,
            'content': 'T',
        }
        r = requests.patch(BASE_URL+'/posts/{}'.format(post['id']), data=options)
        assert r.status_code > 200


    def test_post_edit_long_content(self):
        options = {
            'token': token,
            'content': 'T'*150001,
        }
        r = requests.patch(BASE_URL+'/posts/{}'.format(post['id']), data=options)
        assert r.status_code > 200


    def test_post_edit(self):
        options = {
            'token': token,
            'title': 'Test edit title',
            'blog': blog['id'],
            'content': 'Test edit content',
            'preview_image': 'http://www.otakustudy.com/wp-content/uploads/2014/03/2321.jpg',
        }
        r = requests.patch(BASE_URL+'/posts/{}'.format(post['id']), data=options)
        assert r.status_code == 200
        self.test_post_get_by_location()
        assert post['title'] == options['title']
        assert post['content'] == options['content']
        assert post['blog']['id'] == options['blog']
        assert post['preview_image'] == options['preview_image']


    #
    # Test post delete
    #


    def test_post_delete_without_token(self):
        options = {
        }
        r = requests.delete(BASE_URL+'/posts/{}'.format(post['id']), data=options)
        assert r.status_code > 200

    def test_post_delete_with_token(self):
        options = {
            'token': token,
        }
        r = requests.delete(BASE_URL+'/posts/{}'.format(post['id']), data=options)
        assert r.status_code == 200
