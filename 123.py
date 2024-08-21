import socket
import os

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(local_ip)
    username = os.getlogin()
    print(f"Имя пользователя: {username}")

if __name__ == '__main__':
    get_local_ip()