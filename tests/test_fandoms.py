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
# Add, authenficate and get user.
#


def user_add():
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


def user_authenficate():
    global token
    options = {
        'username': '{}'.format(username),
        'password': '{}'.format(username),
    }
    r = requests.post(BASE_URL+'/token', data=options)
    data = r.json()['data']
    token = data['token']
    assert 'token' in list(data.keys())


def user_get_user_by_user_location():
    global user
    options = {
    }
    r = requests.get(BASE_URL+user_location, data=options)
    data = r.json()['data']
    assert r.status_code == 200
    assert 'user' in data
    user = data['user']


user_add()
user_authenficate()
user_get_user_by_user_location()


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


def test_fandom_edit_title():
    options = {
        'token': token,
        'title': 'Title edit',
    }
    edit_r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert edit_r.status_code == 200

    get_r = requests.get(BASE_URL+'/fandoms/{}'.format(fandom['id']))
    assert get_r.status_code == 200
    get_data = get_r.json()['data']
    assert 'fandom' in list(get_data.keys())
    assert get_data['fandom']['title'] == 'Title edit'


def test_fandom_edit_description():
    options = {
        'token': token,
        'description': 'Description edit',
    }
    edit_r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert edit_r.status_code == 200

    get_r = requests.get(BASE_URL+'/fandoms/{}'.format(fandom['id']))
    assert get_r.status_code == 200
    get_data = get_r.json()['data']
    assert 'fandom' in list(get_data.keys())
    assert get_data['fandom']['description'] == 'Description edit'


def test_fandom_edit_avatar():
    options = {
        'token': token,
        'avatar': 'https://cdn.everypony.ru/storage/03/42/62/2016/06/24/avatar_100x100.png',
    }
    edit_r = requests.patch(BASE_URL+'/fandoms/{}'.format(fandom['id']), data=options)
    assert edit_r.status_code == 200

    get_r = requests.get(BASE_URL+'/fandoms/{}'.format(fandom['id']))
    assert get_r.status_code == 200
    get_data = get_r.json()['data']
    assert 'fandom' in list(get_data.keys())
    assert get_data['fandom']['avatar'] == 'https://cdn.everypony.ru/storage/03/42/62/2016/06/24/avatar_100x100.png'



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


def teardown_module(module):
    requests.get(BASE_URL+'/clearenv')
