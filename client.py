"""
多用户多房间全双工聊天客户端
date : 2016-12-15
author: yaohq
"""

import socket
import time
import sys
import threading

host = 'localhost'
port = 12345
threads = []

def send_data(sock):
    while True:
        data = input('>')
        if data:
            sock.send(data.encode('utf-8'))
        time.sleep(0.2)

def recv_data(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            print('no data')
        else:
            # print(time.strftime('%Y-%m-%d %H:%M:%S') + ' : ' + data.decode('utf-8'))
            print(data.decode('utf-8'))
        time.sleep(0.2)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        try:
            t1 = threading.Thread(target=send_data, args=(s,))
            t2 = threading.Thread(target=recv_data, args=(s,))
            threads.append(t1)
            threads.append(t2)
        except:
            print('create threads failed!')
            sys.exit()

        for t in threads:
            t.start()

        for t in threads:
            t.join()


if __name__ == '__main__':
    main()
