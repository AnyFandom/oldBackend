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


def send_update_comments_request(post_id):
    socketio.emit('update_comments_request', room='post-' + str(post_id))


def send_notification(title, body, id):
    try:
        socketio.emit('notification', {'title': title, 'options': {'body': body}}, room=users[id][0])
        print('Notification Out!')
    except ValueError:
        pass
