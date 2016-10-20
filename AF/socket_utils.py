from AF import socketio
from AF import users


def hi_everyone():
    print(users)
    socketio.emit('my response', 'Hi everyone!', broadcast=True)


def hi_user(id):
    try:
        socketio.emit('my response', 'Hi, ' + str(id), room=users[id][0])
    except ValueError:
        pass


def send_update(type, id=None):
    socketio.emit('update_request', {'type': type, 'id': id})


def send_notification(title, body, id):
    try:
        socketio.emit('notification', {'options': {'title': title, 'body': body}}, room=users[id][0])
        print('Notification Out!')
    except KeyError:
        pass
