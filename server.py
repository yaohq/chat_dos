"""
多用户多房间全双工聊天服务端
date : 2016-12-16
author: yaohq
待修改：
1. 每个房间要有自己单独的发送消息接收消息的线程
2.
"""
import socket
import time
import select
import threading
import sys
import re



host = ''
port = 12345
threads = []  # 线程列表

room = 10  # 定义房间个数，从1到9
room_list = ["%s"%i for i in range(1,room)]  # 房间号，也可以起名字
client_conn = []          # 房间内的客户端连接
data_list = []    # 房间的聊天数据

print(room_list)

for i in room_list:
    client_conn.append([])  #每个房间的socket是一个子列表
    data_list.append([])    # 每个房间的数据是一个子列表

def send_data():
    while True:
        for i in range(len(client_conn)):  # 处理所有房间的循环
            for data in data_list[i]:      # 处理消息队列
                for sock in client_conn[i]: # 处理每个房间内
                    # 不发送给发消息的本人
                    if re.search('(\d+)\)>', str(sock)).group(1) != re.search('\[(\w+)\]', data).group(1):
                        sock.send(data.encode('utf-8'))
                data_list[i].remove(data)

        time.sleep(0.2)


def recv_data():
    while True:
        for i in range(len(client_conn)):
            for sock in client_conn[i]:
                try:
                    data = sock.recv(1024)
                    if not data:
                        print('no data')
                    else:
                        print('[' + re.search('(\d+)\)>', str(sock)).group(1) + '] ' + data.decode('utf-8'))
                        data_list[i].append('[' + re.search('(\d+)\)>', str(sock)).group(1) + '] ' + data.decode('utf-8'))
                except(BlockingIOError):
                    continue
                except ConnectionResetError: # 客户端断开连接，就关闭该连接，然后从socket列表删掉该socket连接
                    sock.close()
                    client_conn[i].remove(sock)

        time.sleep(0.2)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)
        s.setblocking(True)  # 关闭阻塞模式，打开异步，一个客户端连接的recv失败后可以立即退出轮询下一个客户端

        try:
            t1 = threading.Thread(target=send_data)
            t2 = threading.Thread(target=recv_data)
            t1.setDaemon(True)
            t2.setDaemon(True)
            threads.append(t1)
            threads.append(t2)
        except:
            print('create threads failed!')
            sys.exit()

        for t in threads:
            t.start()

        while True:
            rsock, wsock, esock = select.select([s], [], [])
            for sock in rsock:
                if sock is s:
                    """conn应该放到一个列表中，方便管理"""
                    conn, addr = sock.accept()
                    choose = 'please choose a room: ' + ','.join(room_list)
                    conn.send(choose.encode('utf-8'))

                    # 问：这里如何做成阻塞式的？另外，如果一个客户端连接后一直没有发送房间号，另一个客户端连接后怎么办？
                    # 答：轮询，直到客户端发送了房间号码才退出轮询，然后把socket连接放到对应的房间中去
                    while True:
                        try:
                            room_num_str = conn.recv(10)
                            is_rootnum_digit = room_num_str.isdigit()  # 判断客户输入的房间号是否为数字
                            if is_rootnum_digit:
                                room_num = int(room_num_str)  # 如果输入正确，转化为数字
                                break
                        except BlockingIOError:
                            time.sleep(0.1)
                            continue

                    client_conn[room_num-1].append(conn)
                    print('connected by : ', addr)
                    print('room number : ', room_num)
                else:
                    print(sock)
            # print(len(client_conn))


if __name__ == '__main__':
    main()



