# A socket scure proxy ver 5
# Written in python
# ref https://tools.ietf.org/html/rfc1928
from multiprocessing import Process
import threading
import os
import socket
import sys

HOST = None
PORT = 5900
s = None


# ueser passwd
def auth(data):
    pass # TO-DO


# first hand shake
def verfy(conn):
    data = conn.recv(10)
    if data:
        re = None
        if data[0] == 5:  # version 5
            authmethod = {
                0: b'\x05\x00',  # no authmethod
                # 1: b'\x05\xFF',  # not suppported
                2: b'\x05\x01',  # user passwd
            }
            re = authmethod.get(data[2], b'\x05\x0FF')
            conn.send(re)
            if data[2] == 2:
                return auth(data)
            if data[2] == 0:
                return 1
    return None


# second hand shake
def getrequest(conn):
    data = conn.recv(512)  # the acture size should be less than 261 bytes
    addtype = {
        # ipv4
        1: lambda data: ('.'.join(int(data[x]) for x in range(4, 7)), int.from_bytes(data[-2:], byteorder='big', signed=False), socket.AF_INET),
        # domain name
        3: lambda data: ((data[5: 5 + data[4]]).decode("utf-8"), int.from_bytes(data[-2:], byteorder='big', signed=False), socket.AF_UNSPEC),
        # ipv6
        4: lambda data: (':'.join(''.join(format(data[x * 2:x * 2 + 1], '{:02x}') for x in range(2, 9))), int.from_bytes(data[-2:], byteorder='big', signed=False), socket.AF_INET6),
    }
    host, port, adtype = addtype.get(data[3], lambda: None)(data)
    client = None
    re = bytearray(data)
    re[1] = 0
    # try to connect to the remote server
    for res in socket.getaddrinfo(host, port, adtype, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            client = socket.socket(af, socktype, proto)
        except OSError as msg:
            print (msg)
            client = None
            continue
        try:
            client.connect(sa)
        except OSError as msg:
            print (msg)
            client.close()
            client = None
            continue
        break
    if client is None:
        re[1] = 1  # if failed
    conn.send(re)  # response
    return client


def trans(client, host):
    data = client.recv(4096)
    while data:
        try:
            host.send(data)
            data = client.recv(4096)
        except OSError as msg:
            break


# a process to run when a connection comes in
def host_pro(conn, addr):
    print('connected by', addr)
    if verfy(conn):
        client = getrequest(conn)
        if client:
            t1 = threading.Thread(target=trans, args=(conn, client,))
            t2 = threading.Thread(target=trans, args=(client, conn,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            client.close()
    print('close connection from', addr)
    conn.close()


# The main function
if __name__ == '__main__':
    # list all avaiable interfaces and try to on the port
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except OSError as msg:
            s = None
            continue  # if failed, continue trying a new interface
        try:
            s.bind(sa)
            s.listen(1)
        except OSError as msg:
            s.close()
            s = None
            continue
        break  # if success break the loop
    if s is None:
        print('Port %s cannot open, is it occupied ?' % PORT)
        sys.exit(1)  # Port Occupied exit
    print('init success, waiting on ', PORT)
    while 1:
        conn, addr = s.accept()  # Listen the port if a connection comes in
        p = threading.Thread(target=host_pro, args=(conn, addr,)) # mutil thread method
        # p = Process(target=host_pro, args=(conn, addr,)) # mutil process mehod
        p.start()  # run the process
