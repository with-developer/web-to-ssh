from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import paramiko
import select

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Key: SocketIO SID, Value: paramiko.SSHClient and Channel instances
ssh_clients = {}

def read_until_prompt(channel, prompts):
    output = b""
    while True:
        rlist, _, _ = select.select([channel], [], [], 1)
        if rlist:
            recv_chunk = channel.recv(1024)
            output += recv_chunk
            for prompt in prompts:
                if output.decode('utf-8', errors='ignore').endswith(prompt):
                    return output.decode('utf-8', errors='ignore')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname='172.20.10.2', port=5006, username='user2', password='1234')
        chan = ssh_client.invoke_shell()
        ssh_clients[request.sid] = {'client': ssh_client, 'channel': chan}
    except Exception as e:
        emit('new_output', {'output': f"Error connecting to SSH: {str(e)}"})

@socketio.on('send_command')
def handle_command(data):
    command = data['command']
    print("command:",command)
    session_data = ssh_clients.get(request.sid)
    
    if not session_data:
        emit('new_output', {'output': "No SSH connection"})
        return
    
    chan = session_data['channel']
    try:
        chan.send(command + '\n')
        output = read_until_prompt(chan, prompts=['$ ', '# '])
        cleaned_output = output[len(command) + 1:]
        emit('new_output', {'output': cleaned_output})
    except Exception as e:
        emit('new_output', {'output': f"Error executing command: {str(e)}"})

@socketio.on('disconnect')
def handle_disconnect():
    session_data = ssh_clients.pop(request.sid, None)
    if session_data:
        session_data['channel'].close()
        session_data['client'].close()

if __name__ == '__main__':
    socketio.run(app)
