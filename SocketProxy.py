from multiprocessing import Process
import os
import socket
import sys

HOST = None
PORT = 5900
s = None

# a process to run when a connection comes in


def host_pro(conn, addr):
    print('connected by ', addr)
    if verfy(conn):
        while 1:
            data = conn.recv(1024)
            if not data:
                break
    conn.close()


def verfy(conn):
    data = conn.recv(1024)
    if data:
        re = None
        if data[0] == 5:  # version 5
            authmethod = {
                0: b'\x05\x00',  # no authmethod
                1: b'\x05\xFF',  # not suppported
                2: b'\x05\x01'  # user passwd
            }

    return None


def auth(data):

    # The main function
if __name__ == '__main__':
    # list all avaiable interfaces and try to on the port
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except OSError as msg:
            s = None
            continue  # if failed continue trying a new interface
        try:
            s.bind(sa)
            s.listen(1)
        except OSError as msg:
            s.close()
            s = None
            continue
        break  # if success break and continue
    if s is None:
        print('Port %s cannot open, is it occupied ?' % (PORT))
        sys.exit(1)  # Port Occupied exit
    while 1:
        conn, addr = s.accept()  # Listen the port if a connection comes in
        p = Process(target=host_pro, args=(conn, addr,))
        p.start()  # run the process
