import socket, threading, time, argparse


class Server(object):

    def __init__(self, host, port):
        print("Server starting......")
        self.host = host
        self.port = port
        self.s_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s_s.bind((host, port))
        self.s_s.listen(20)

    def start(self):
        while True:
            try:
                conn, addr = self.s_s.accept()
                threading.Thread(target=s2c, args=[conn]).start()
            except Exception as e:
                print(str(e))
                print("\nExcept happened")


def s2c(connect_socket):
    all_src_data, hostname, port, ssl = get_host_header(connect_socket)
    connect, response = get_data_from_host(hostname, port, all_src_data, ssl)
    if ssl:
        response = b"HTTP/1.0 200 Connection Established\r\n\r\n"
    csc(connect_socket, connect, response)


def get_host_header(s):
    while True:
        header = s.recv(1024)
        if header:
            _header = header.split()
            if b'CONNECT' == _header[0]:
                return header, _header[1].decode().split(':')[0], 443, True
            if len(str(_header[4]).split(':')) == 2:
                port = int(str(_header[4]).split(':')[1])
                hostname = str(_header[4]).split(':')[0]
            else:
                port = 80
                hostname = _header[4].decode()
            return header, str(hostname), port, False


def get_data_from_host(host, port, data, ssl):
    connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect.connect((host, port))
    if ssl:
        return connect, ''
    else:
        connect.sendall(data)
    return connect, connect.recv(10240)


def csc(from_connect, to_connect, response):
    from_connect.sendall(response)

    thread_list = []

    t1 = threading.Thread(target=cs, args=(from_connect, to_connect))
    t2 = threading.Thread(target=sc, args=(from_connect, to_connect))
    thread_list.append(t1)
    thread_list.append(t2)
    for t in thread_list:
        t.start()
    while not to_connect._closed:
        time.sleep(1)
    from_connect.close()


def cs(f, t):
    try:
        while True:
            response = f.recv(1024)
            if response:
                t.sendall(response)

            else:
                f.close()
    except:
        f.close()
        t.close()


def sc(f, t):
    try:
        while True:
            response = t.recv(1024)
            if response:
                f.sendall(response)
    except:
        t.close()
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is a proxy for Python3')
    parser.add_argument('-p', '--port', type=int, dest='p', help='The proxy port')

    args = parser.parse_args()

    if not args.p:
        raise ValueError('Please do proxy -h')

    Server("0.0.0.0", args.p).start()
