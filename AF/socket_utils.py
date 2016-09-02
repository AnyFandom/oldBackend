from AF import socketio

def say_hi():
    socketio.emit('my response', 'Hi everyone!', broadcast=True)
