import pytest
import requests
from conf import BASE_URL

token = ''
user_location = ''
username = 'unittest-fandoms'
user = {}

fandom = {}
fandom_location = {}
#
# Test add, authenficate and get user.
#


def test_user_add():
    global user_location
    options = {
        'username': '{}'.format(username),
        'password': '{}'.format(username),
    }

    r = requests.post(BASE_URL+'/users', data=options)
    data = r.json()
    assert r.status_code == 201
    assert 'Location' in list(data['data'].keys())
    user_location = data['data']['Location']


def test_user_authenficate():
    global token
    options = {
        'username': '{}'.format(username),
        'password': '{}'.format(username),
    }
    r = requests.post(BASE_URL+'/token', data=options)
    data = r.json()['data']
    token = data['token']
    assert 'token' in list(data.keys())


def test_user_get_user_by_user_location():
    global user
    options = {
    }
    r = requests.get(BASE_URL+user_location, data=options)
    data = r.json()['data']
    assert r.status_code == 200
    assert 'user' in data
    user = data['user']


#
# Test add fandom
#

def test_fandom_add_without_token():
    global fandom_location
    options = {
        'title': 'Unittest with avatar fandom title',
        'description': 'Unittest fandom description',
        'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
    }
    r = requests.post(BASE_URL+'/fandoms', data=options)
    assert r.status_code != 201


def test_fandom_add_without_avatar():
    global fandom_location
    options = {
        'token': token,
        'title': 'Unittest without avatar fandom title',
        'description': 'Unittest fandom description',
    }
    r = requests.post(BASE_URL+'/fandoms', data=options)
    data = r.json()['data']
    assert r.status_code == 201
    assert 'Location' in list(data.keys())
    fandom_location = data['Location']


def test_fandom_add_without_title():
    global fandom_location
    options = {
        'token': token,
        'description': 'Unittest fandom description',
        'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
    }
    r = requests.post(BASE_URL+'/fandoms', data=options)
    assert r.status_code != 201


def test_fandom_add_without_description():
    global fandom_location
    options = {
        'token': token,
        'title': 'Unittest without description fandom title',
        'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
    }
    r = requests.post(BASE_URL+'/fandoms', data=options)
    data = r.json()['data']
    assert r.status_code == 201
    assert 'Location' in list(data.keys())
    fandom_location = data['Location']


def test_fandom_add_with_short_title():
    global fandom_location
    options = {
        'token': token,
        'title': 'u',
        'description': 'Unittest fandom description',
        'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
    }
    r = requests.post(BASE_URL+'/fandoms', data=options)
    assert r.status_code != 201


def test_fandom_add_with_long_title():
    global fandom_location
    options = {
        'token': token,
        'title': 'u'*201,
        'description': 'Unittest fandom description',
        'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
    }
    r = requests.post(BASE_URL+'/fandoms', data=options)
    assert r.status_code != 201


def test_fandom_add_with_long_description():
    global fandom_location
    options = {
        'token': token,
        'title': 'Unittest fandom with long description',
        'description': 'U'*5001,
        'avatar': 'https://static.lunavod.ru/img/users/60/avatar_100x100.png'
    }
    r = requests.post(BASE_URL+'/fandoms', data=options)
    assert r.status_code != 201


def test_fandom_add():
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





#
# Test get fandom
#


def test_fandom_get_by_location():
    global fandom
    options = {
    }
    r = requests.get(BASE_URL+fandom_location, params=options)
    data = r.json()['data']
    assert r.status_code == 200
    assert 'fandom' in list(data.keys())
    fandom = data['fandom']


def test_fandom_get_by_id():
    options = {
    }
    r = requests.get(BASE_URL+'/fandoms/{}'.format(fandom['id']), params=options)
    data = r.json()['data']
    assert r.status_code == 200
    assert 'fandom' in list(data.keys())


#
# Test edit fandom
#


def test_fandom_edit_without_token():
    options = {
    }
    r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert r.status_code != 200


def test_fandom_edit_with_token():
    options = {
        'token': token,
    }
    r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert r.status_code == 200


def test_fandom_edit_short_title():
    options = {
        'token': token,
        'title': 'u',
    }
    r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert r.status_code != 200


def test_fandom_edit_long_title():
    options = {
        'token': token,
        'title': 'u'*201,
    }
    r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert r.status_code != 200


def test_fandom_edit_long_description():
    options = {
        'token': token,
        'description': 'u'*5001,
    }
    r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert r.status_code != 200


#
# Test delete fandom
#


def test_fandom_delete_without_token():
    options = {
    }
    r = requests.delete(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert r.status_code != 200


def test_fandom_delete_with_token():
    options = {
        'token': token
    }
    r = requests.delete(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert r.status_code != 200


#
# Test delete user
#

def test_user_delete():
    options = {
        'token': token,
    }
    r = requests.delete(BASE_URL+'/users/id/{}'.format(user['id']), params=options)
    print(r.json())
    assert r.status_code == 200


def teardown_module(module):
    requests.get(BASE_URL+'/clearenv')
