from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import paramiko
import select

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Key: SocketIO SID, Value: paramiko.SSHClient instance
ssh_clients = {}
command_buffer = {}  # Key: SocketIO SID, Value: Command buffer

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname='127.0.0.1', port=5006, username='user2', password='1234')
        
        ssh_clients[request.sid] = ssh_client
        command_buffer[request.sid] = ""
    except Exception as e:
        emit('new_output', {'output': f"Error connecting to SSH: {str(e)}"})

@socketio.on('send_command')
def handle_command(data):
    command = data['command']
    emit('new_output', {'output': command})
    ssh_client = ssh_clients.get(request.sid)
    
    if not ssh_client:
        emit('new_output', {'output': "No SSH connection"})
        return

    command_buffer[request.sid] += command

    if '\r' in command_buffer[request.sid]:
        print("catch enter!")
        print("command_buffer:",command_buffer[request.sid])
        try:
            actual_command = command_buffer[request.sid].strip()
            stdin, stdout, stderr = ssh_client.exec_command(actual_command + '\n')
            print("stdin:",stdin)
            
            while not stdout.channel.exit_status_ready():
                #print("while not")
                # Only print data if there is data to read in the channel
                if stdout.channel.recv_ready():
                    print("ready")
                    rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                    if len(rl) > 0:
                        # Print data from stdout
                        output = stdout.channel.recv(1024).decode('utf-8').strip()
                        if output:
                            print("output:",output)
                            emit('new_output', {'output': output})
                        else:
                            print("not existed output data")
            
            command_buffer[request.sid] = ""
        except Exception as e:
            emit('new_output', {'output': f"Error executing command: {str(e)}"})

@socketio.on('disconnect')
def handle_disconnect():
    ssh_client = ssh_clients.pop(request.sid, None)
    command_buffer.pop(request.sid, None)
    if ssh_client:
        ssh_client.close()

if __name__ == '__main__':
    socketio.run(app, debug=True)
