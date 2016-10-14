import pytest
import requests
from conf import BASE_URL

requests.get(BASE_URL+'/clearenv')
token = ''
user_location = ''
username = 'unittest-fandoms'
user = {}

fandom = {}
fandom_location = {}

blog = {}
blog_location = {}


def setup_module(module):
    requests.get(BASE_URL+'/clearenv')


def teardown_module(module):
    requests.get(BASE_URL+'/clearenv')


class TestBlogs():
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


    def test_init(self):
        self.user_add()
        self.user_authenficate()
        self.user_get_user_by_user_location()
        self.fandom_add()
        self.fandom_get_by_location()


    def test_blog_add_without_token(self):
        options = {
        }
        r = requests.post(BASE_URL+'/blogs', data=options)
        assert r.status_code != 201


    def test_blog_add_without_title(self):
        options = {
            'token': token,
            'fandom': fandom['id'],
        }
        r = requests.post(BASE_URL+'/blogs', data=options)
        assert r.status_code != 201


    def test_blog_add_with_short_title(self):
        options = {
            'token': token,
            'fandom': fandom['id'],
            'title': 'u',
        }
        r = requests.post(BASE_URL+'/blogs', data=options)
        assert r.status_code != 201


    def test_blog_add_with_long_title(self):
        options = {
            'token': token,
            'fandom': fandom['id'],
            'title': 'u'*201,
        }
        r = requests.post(BASE_URL+'/blogs', data=options)
        assert r.status_code != 201


    def test_blog_add_with_long_description(self):
        options = {
            'token': token,
            'fandom': fandom['id'],
            'title': 'Test',
            'description': 'u'*5001,
        }
        r = requests.post(BASE_URL+'/blogs', data=options)
        assert r.status_code != 201


    def test_blog_add_without_fandom(self):
        options = {
            'token': token,
            'title': 'Test',
            'description': 'Test',
        }
        r = requests.post(BASE_URL+'/blogs', data=options)
        assert r.status_code != 201


    def test_blog_add(self):
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


    #
    # Test get blog
    #


    def test_blog_get_by_location(self):
        global blog
        options = {
        }
        r = requests.get(BASE_URL+blog_location)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'blog' in list(data.keys())
        blog = data['blog']


    def test_blog_get_by_id(self):
        options = {
        }
        r = requests.get(BASE_URL+'/blogs/{}'.format(blog['id']))
        assert r.status_code == 200
        data = r.json()['data']
        assert 'blog' in list(data.keys())


    #
    # Test edit blog
    #


    def test_blog_edit_without_token(self):
        options = {
        }
        r = requests.patch(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert r.status_code != 200


    def test_blog_edit_with_token(self):
        options = {
            'token': token,
        }
        r = requests.patch(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert r.status_code == 200


    def test_blog_edit_short_title(self):
        options = {
            'token': token,
            'title': 'u',
        }
        r = requests.patch(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert r.status_code != 200


    def test_blog_edit_long_title(self):
        options = {
            'token': token,
            'title': 'u'*201,
        }
        r = requests.patch(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert r.status_code != 200


    def test_blog_edit_long_description(self):
        options = {
            'token': token,
            'description': 'u'*5001,
        }
        r = requests.patch(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert r.status_code != 200


    def test_blog_edit_title(self):
        options = {
            'token': token,
            'title': 'Title edit',
        }
        edit_r = requests.patch(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert edit_r.status_code == 200

        get_r = requests.get(BASE_URL+'/blogs/{}'.format(blog['id']))
        assert get_r.status_code == 200
        get_data = get_r.json()['data']
        assert 'blog' in list(get_data.keys())
        assert get_data['blog']['title'] == 'Title edit'


    def test_blog_edit_description(self):
        options = {
            'token': token,
            'description': 'Description edit',
        }
        edit_r = requests.patch(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert edit_r.status_code == 200

        get_r = requests.get(BASE_URL+'/blogs/{}'.format(blog['id']))
        assert get_r.status_code == 200
        get_data = get_r.json()['data']
        assert 'blog' in list(get_data.keys())
        assert get_data['blog']['description'] == 'Description edit'


    def test_blog_edit_avatar(self):
        options = {
            'token': token,
            'avatar': 'https://cdn.everypony.ru/storage/03/42/62/2016/06/24/avatar_100x100.png',
        }
        edit_r = requests.patch(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert edit_r.status_code == 200

        get_r = requests.get(BASE_URL+'/blogs/{}'.format(blog['id']))
        assert get_r.status_code == 200
        get_data = get_r.json()['data']
        assert 'blog' in list(get_data.keys())
        assert get_data['blog']['avatar'] == 'https://cdn.everypony.ru/storage/03/42/62/2016/06/24/avatar_100x100.png'


    #
    # Test delete blog
    #


    def test_blog_delete_without_token(self):
        options = {
        }
        r = requests.delete(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert r.status_code != 200


    def test_blog_delete_with_token(self):
        options = {
            'token': token
        }
        r = requests.delete(BASE_URL+'/blogs/{}'.format(blog['id']), data=options)
        assert r.status_code != 200
