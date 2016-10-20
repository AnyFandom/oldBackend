import pytest
import requests
from conf import BASE_URL

token = ''
user_location = ''
username = 'unittest-fandoms'
user = {}

fandom = {}
fandom_location = ''


def setup_module(module):
    requests.get(BASE_URL+'/clearenv')


def teardown_module(module):
    requests.get(BASE_URL+'/clearenv')

class TestFandoms():
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
        assert 'token' in data


    def user_get_user_by_user_location(self):
        global user
        options = {
        }
        r = requests.get(BASE_URL+user_location, data=options)
        data = r.json()['data']
        assert r.status_code == 200
        assert 'user' in data
        user = data['user']


    def test_init(self):
        self.user_add()
        self.user_authenficate()
        self.user_get_user_by_user_location()


    #
    # Test add fandom
    #

    def test_fandom_add_without_token(self):
        global fandom_location
        options = {
            'title': 'Unittest with avatar fandom title',
            'description': 'Unittest fandom description',
            'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
        }
        r = requests.post(BASE_URL+'/fandoms', data=options)
        assert r.status_code != 201


    def test_fandom_add_without_avatar(self):
        global fandom_location
        options = {
            'token': token,
            'title': 'Unittest without avatar fandom title',
            'description': 'Unittest fandom description',
        }
        r = requests.post(BASE_URL+'/fandoms', data=options)
        data = r.json()['data']
        assert r.status_code == 201
        assert 'Location' in data
        fandom_location = data['Location']


    def test_fandom_add_without_title(self):
        global fandom_location
        options = {
            'token': token,
            'description': 'Unittest fandom description',
            'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
        }
        r = requests.post(BASE_URL+'/fandoms', data=options)
        assert r.status_code != 201


    def test_fandom_add_without_description(self):
        global fandom_location
        options = {
            'token': token,
            'title': 'Unittest without description fandom title',
            'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
        }
        r = requests.post(BASE_URL+'/fandoms', data=options)
        data = r.json()['data']
        assert r.status_code == 201
        assert 'Location' in data
        fandom_location = data['Location']


    def test_fandom_add_with_short_title(self):
        global fandom_location
        options = {
            'token': token,
            'title': 'u',
            'description': 'Unittest fandom description',
            'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
        }
        r = requests.post(BASE_URL+'/fandoms', data=options)
        assert r.status_code != 201


    def test_fandom_add_with_long_title(self):
        global fandom_location
        options = {
            'token': token,
            'title': 'u'*201,
            'description': 'Unittest fandom description',
            'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
        }
        r = requests.post(BASE_URL+'/fandoms', data=options)
        assert r.status_code != 201


    def test_fandom_add_with_long_description(self):
        global fandom_location
        options = {
            'token': token,
            'title': 'Unittest fandom with long description',
            'description': 'U'*5001,
            'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
        }
        r = requests.post(BASE_URL+'/fandoms', data=options)
        assert r.status_code != 201


    def test_fandom_add(self):
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
        assert 'Location' in data
        fandom_location = data['Location']





    #
    # Test get fandom
    #


    def test_fandom_get_by_location(self):
        global fandom
        options = {
        }
        r = requests.get(BASE_URL+fandom_location, params=options)
        data = r.json()['data']
        assert r.status_code == 200
        assert 'fandom' in data
        fandom = data['fandom']


    def test_fandom_get_by_id(self):
        options = {
        }
        r = requests.get(BASE_URL+'/fandoms/{}'.format(fandom['id']), params=options)
        data = r.json()['data']
        assert r.status_code == 200
        assert 'fandom' in data


    def test_fandom_get_from_list(self):
        options = {
        }
        r = requests.get(BASE_URL+'/fandoms', params=options)
        assert r.status_code == 200
        data = r.json()['data']
        assert 'fandoms' in data
        fandoms = [f['id'] for f in data['fandoms']]
        assert fandom['id'] in fandoms


    #
    # Test edit fandom
    #


    def test_fandom_edit_without_token(self):
        options = {
        }
        r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert r.status_code != 200


    def test_fandom_edit_with_token(self):
        options = {
            'token': token,
        }
        r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert r.status_code == 200


    def test_fandom_edit_short_title(self):
        options = {
            'token': token,
            'title': 'u',
        }
        r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert r.status_code != 200


    def test_fandom_edit_long_title(self):
        options = {
            'token': token,
            'title': 'u'*201,
        }
        r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert r.status_code != 200


    def test_fandom_edit_long_description(self):
        options = {
            'token': token,
            'description': 'u'*5001,
        }
        r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert r.status_code != 200


    def test_fandom_edit_title(self):
        options = {
            'token': token,
            'title': 'Title edit',
        }
        edit_r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert edit_r.status_code == 200

        get_r = requests.get(BASE_URL+'/fandoms/{}'.format(fandom['id']))
        assert get_r.status_code == 200
        get_data = get_r.json()['data']
        assert 'fandom' in get_data
        assert get_data['fandom']['title'] == 'Title edit'


    def test_fandom_edit_description(self):
        options = {
            'token': token,
            'description': 'Description edit',
        }
        edit_r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert edit_r.status_code == 200

        get_r = requests.get(BASE_URL+'/fandoms/{}'.format(fandom['id']))
        assert get_r.status_code == 200
        get_data = get_r.json()['data']
        assert 'fandom' in get_data
        assert get_data['fandom']['description'] == 'Description edit'


    def test_fandom_edit_avatar(self):
        options = {
            'token': token,
            'avatar': 'https://cdn.everypony.ru/storage/03/42/62/2016/06/24/avatar_100x100.png',
        }
        edit_r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert edit_r.status_code == 200

        get_r = requests.get(BASE_URL+'/fandoms/{}'.format(fandom['id']))
        assert get_r.status_code == 200
        get_data = get_r.json()['data']
        assert 'fandom' in get_data
        assert get_data['fandom']['avatar'] == 'https://cdn.everypony.ru/storage/03/42/62/2016/06/24/avatar_100x100.png'



    #
    # Test delete fandom
    #


    def test_fandom_delete_without_token(self):
        options = {
        }
        r = requests.delete(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert r.status_code != 200


    def test_fandom_delete_with_token(self):
        options = {
            'token': token
        }
        r = requests.delete(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
        assert r.status_code == 200
