from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import emit
import logging

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_command')
def handle_command(json):
    command = json['command']
    print(command)
    # 여기서 실제 명령어 처리 로직을 구현합니다.
    emit('new_output', {'output': command})

if __name__ == '__main__':
    socketio.run(app)
