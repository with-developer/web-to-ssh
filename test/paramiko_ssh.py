import paramiko
import getpass
import readline

def read_until_prompt(channel, prompt='$ '):
    output = ""
    while not output.endswith(prompt):
        output += channel.recv(1024).decode('utf-8')
    return output

def my_input(prompt):
    line = input(prompt)
    if '\t' in line:
        channel.send(line + '\n')
        suggestions = read_until_prompt(channel)
        print(suggestions)
        line = my_input(prompt)
    return line

hostname = '172.20.10.2'
port = 5006
ID = input("Username: ")
PASSWD = getpass.getpass("Password: ")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=hostname, port=port, username=ID, password=PASSWD)

# 쉘 채널 열기
channel = ssh.invoke_shell()

# 초기 메시지를 출력
init_message = read_until_prompt(channel)
print(init_message, end="")

while True:
    command = my_input('$ ')  # readline과 함께 사용
    if command == "exit()":
        channel.close()
        ssh.close()
        break
    else:
        channel.send(command + '\n')
        output = read_until_prompt(channel)
        cleaned_output = output[len(command) + 2:]
        print(cleaned_output, end="")
