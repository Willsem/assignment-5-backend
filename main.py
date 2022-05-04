import os
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, send, emit, rooms


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
CORS(app)
ws = SocketIO(app, cors_allowed_origins='*')

all_rooms = {}
texts = dict()

@ws.on('join')
def on_join(room):
    join_room(room)
    if not room in texts.keys():
        texts[room] = ''
    send({ 'text': texts[room] }, room=room)
    all_rooms.setdefault(room, 0)
    all_rooms[room] += 1

@ws.on('leave')
def on_leave(room):
    leave_room(room)
    all_rooms[room] -= 1
    if all_rooms[room] == 0:
        all_rooms.pop(room)

@ws.on('update')
def on_message(msg):
    # broadcast to everyone in the same room on the 'message' channel
    my_rooms = rooms() # get all rooms of this user
    my_rooms.remove(request.sid) # remove personal room
    emit(
        'text', 
        { 'text': msg },
        room=my_rooms[-1],
        json=True
    )

@app.route('/rooms')
def list_rooms():
    return jsonify(list(all_rooms.keys()))


if __name__ == '__main__':
    ws.run(
        app,
        host='0.0.0.0', # listen to outside requests 
        port=int(os.getenv('PORT', '5000')),
        debug=True,
    )
