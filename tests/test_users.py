import pytest
import requests
from conf import BASE_URL

token = ''
token_new = ''
location = ''
user = {}

#
# Test user add
#


def test_user_add_without_username():
    options = {
        'password': 'unittest-users',
    }

    r = requests.post(BASE_URL+'/users', data=options)
    data = r.json()
    assert r.status_code != 201


def test_user_add_with_short_username():
    options = {
        'username': 'un',
        'password': 'unittest-users',
    }

    r = requests.post(BASE_URL+'/users', data=options)
    data = r.json()
    assert r.status_code != 201


def test_user_add_with_long_username():
    options = {
        'username': 'u'*51,
        'password': 'unittest-users',
    }

    r = requests.post(BASE_URL+'/users', data=options)
    data = r.json()
    assert r.status_code != 201


def test_user_add_without_password():
    options = {
        'username': 'unittest-users',
    }

    r = requests.post(BASE_URL+'/users', data=options)
    data = r.json()
    assert r.status_code != 201


def test_user_add_with_short_password():
    options = {
        'username': 'unittest-users',
        'password': 'un',
    }

    r = requests.post(BASE_URL+'/users', data=options)
    data = r.json()
    assert r.status_code != 201


def test_user_add_with_long_password():
    options = {
        'username': 'unettest',
        'password': 'u'*201,
    }

    r = requests.post(BASE_URL+'/users', data=options)
    data = r.json()
    assert r.status_code != 201


def test_user_add():
    global location
    options = {
        'username': 'unittest-users',
        'password': 'unittest-users',
    }

    r = requests.post(BASE_URL+'/users', data=options)
    data = r.json()
    assert r.status_code == 201
    assert 'Location' in list(data['data'].keys())
    location = data['data']['Location']


#
# Test user authenficate
#


def test_user_authenficate_without_username():
    options = {
        'password': 'unittest-users',
    }
    r = requests.post(BASE_URL+'/token', data=options)
    data = r.json()
    assert data['status'] != 'success'


def test_user_authenficate_wrong_username():
    options = {
        'username': 'unittest-users_wrong',
        'password': 'unittest-users',
    }
    r = requests.post(BASE_URL+'/token', data=options)
    data = r.json()
    assert data['status'] != 'success'


def test_user_authenficate_without_password():
    options = {
        'username': 'unittest-users',
    }
    r = requests.post(BASE_URL+'/token', data=options)
    data = r.json()
    assert data['status'] != 'success'


def test_user_authenficate_wrong_password():
    options = {
        'username': 'unittest-users',
        'password': 'unittest-users_wrong',
    }
    r = requests.post(BASE_URL+'/token', data=options)
    data = r.json()
    assert data['status'] != 'success'


def test_user_authenficate():
    global token
    options = {
        'username': 'unittest-users',
        'password': 'unittest-users',
    }
    r = requests.post(BASE_URL+'/token', data=options)
    data = r.json()['data']
    token = data['token']
    assert 'token' in list(data.keys())


#
# Test user get
#


def test_user_get_user_by_location():
    global user
    options = {
    }
    r = requests.get(BASE_URL+location, data=options)
    data = r.json()['data']
    assert r.status_code == 200
    assert 'user' in data
    user = data['user']



def test_user_get_by_id():
    options = {
    }
    print(user)
    r = requests.get(BASE_URL+'/users/id/{}'.format(user['id']), data=options)
    assert r.status_code == 200


def test_user_get_by_id_with_token():
    options = {
        'token': token
    }
    r = requests.get(BASE_URL+'/users/id/{}'.format(user['id']), data=options)
    assert r.status_code == 200


def test_user_get_by_username():
    options = {
    }
    r = requests.get(BASE_URL+'/users/profile/unittest-users', data=options)
    assert r.status_code == 200


def test_user_get_by_id_with_token():
    options = {
        'token': token
    }
    r = requests.get(BASE_URL+'/users/profile/unittest-users', data=options)
    assert r.status_code == 200


#
# Test user current
#
def test_user_get_current_without_token():
    options = {
    }
    r = requests.get(BASE_URL+'/users/current', params=options)
    assert r.status_code != 200


def test_user_get_current_with_token():
    options = {
        'token': token,
    }
    r = requests.get(BASE_URL+'/users/current', params=options)
    print(r.json(), token)
    assert r.status_code == 200


#
# Test user edit
#


def test_user_edit_by_id_without_token():
    options = {
    }
    r = requests.patch(BASE_URL+'/users/id/{}'.format(user['id']), data=options)
    data = r.json()
    assert data['status'] != 'success'


def test_user_edit_by_id():
    options = {
        'token': token,
    }
    r = requests.patch(BASE_URL+'/users/id/{}'.format(user['id']), data=options)
    data = r.json()
    assert data['status'] == 'success'


def test_user_edit_by_username_without_token():
    options = {
    }
    r = requests.patch(BASE_URL+'/users/profile/unittest-users', data=options)
    data = r.json()
    assert data['status'] != 'success'


def test_user_edit_by_username():
    options = {
        'token': token,
    }
    r = requests.patch(BASE_URL+'/users/profile/unittest-users', data=options)
    data = r.json()
    assert data['status'] == 'success'


def test_user_edit_avatar():
    options = {
        'token': token,
        'avatar': 'https://cdn.everypony.ru/storage/03/42/62/2016/06/24/avatar_100x100.png',
    }
    r_edit = requests.patch(BASE_URL+'/users/id/{}'.format(user['id']), data=options)
    data_edit = r_edit.json()

    r_get = requests.get(BASE_URL+'/users/id/{}'.format(user['id']))
    data_get = r_get.json()
    data_edit = r_edit.json()
    assert data_edit['status'] == 'success'
    assert data_get['status'] == 'success'
    assert data_get['data']['user']['avatar'] == 'https://cdn.everypony.ru/storage/03/42/62/2016/06/24/avatar_100x100.png'


def test_user_edit_description_with_long_description():
    options = {
        'description': 'u'*5001
    }
    r = requests.patch(BASE_URL+'/users/profile/unittest-users', data=options)
    data = r.json()
    assert data['status'] != 'success'


def test_user_edit_description():
    options = {
        'token': token,
        'description': 'Description text',
    }
    r_edit = requests.patch(BASE_URL+'/users/id/{}'.format(user['id']), data=options)
    data_edit = r_edit.json()

    r_get = requests.get(BASE_URL+'/users/id/{}'.format(user['id']))
    data_get = r_get.json()
    data_edit = r_edit.json()
    assert data_edit['status'] == 'success'
    assert data_get['status'] == 'success'
    assert data_get['data']['user']['description'] == 'Description text'


def test_user_edit_password_with_wrong_old_password():
    options = {
        'token': token,
        'password': 'un',
        'new_password': 'unittest-users_new'
    }
    r = requests.patch(BASE_URL+'/users/profile/unittest-users', data=options)
    data = r.json()
    assert data['status'] != 'success'


def test_user_edit_password_with_short_password():
    options = {
        'token': token,
        'password': 'unittest-users',
        'new_password': 'un'
    }
    r = requests.patch(BASE_URL+'/users/profile/unittest-users', data=options)
    data = r.json()
    print(data)
    assert data['status'] != 'success'


def test_user_edit_password_with_long_password():
    options = {
        'token': token,
        'password': 'unittest-users',
        'new_password': 'u'*201
    }
    r = requests.patch(BASE_URL+'/users/profile/unittest-users', data=options)
    data = r.json()
    print(data)
    assert data['status'] != 'success'


def test_user_edit_password():
    options = {
        'token': token,
        'password': 'unittest-users',
        'new_password': 'unittest-users_new'
    }
    r = requests.patch(BASE_URL+'/users/profile/unittest-users', data=options)
    data = r.json()
    assert data['status'] == 'success'


#
# Test authenficate with new password
#


def test_user_authenficate_with_new_password():
    global token_new
    options = {
        'username': 'unittest-users',
        'password': 'unittest-users_new',
    }
    r = requests.post(BASE_URL+'/token', data=options)
    data = r.json()['data']
    token_new = data['token']
    assert 'token' in list(data.keys())


#
# Test user delete
#


def test_user_delete_without_token():
    options = {
    }
    r = requests.delete(BASE_URL+'/users/id/{}'.format(user['id']), params=options)
    assert r.status_code != 200


def test_user_delete_with_old_token():
    options = {
        'token': token,
    }
    r = requests.delete(BASE_URL+'/users/id/{}'.format(user['id']), params=options)
    assert r.status_code != 200


def test_user_delete():
    options = {
        'token': token_new,
    }
    r = requests.delete(BASE_URL+'/users/id/{}'.format(user['id']), params=options)
    print(r.json())
    assert r.status_code == 200


def teardown_module(module):
    requests.get(BASE_URL+'/clearenv')
