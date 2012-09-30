import zmq
import socket
import hiredis


class Service:

    def __init__(self):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect('tmp/redis.sock')
        self.hiredis = hiredis.Reader()

    def hello_redis(self):
        self.socket.send(
            b'*2\r\n$4\r\nINCR\r\n$19\r\nredis_hello_counter\r\n')
        while True:
            chunk = self.socket.recv(4096)
            if not chunk:
                raise RuntimeError('Connection closed')
            self.hiredis.feed(chunk)
            data = self.hiredis.gets()
            if data is not False:
                break
        return str(data)


def main():
    svc = Service()
    ctx = zmq.Context()
    sock = ctx.socket(zmq.REP)
    sock.connect("ipc://./tmp/zgw.sock")
    while True:
        uri, = sock.recv_multipart()
        mname = uri.decode('ascii').strip('/_')
        try:
            meth = getattr(svc, mname)
        except AttributeError:
            sock.send_multipart([b'404 Not Found', b'<h1>404 Not Found</h1>'])
        else:
            res = meth()
            sock.send_multipart([res.encode('ascii')])


if __name__ == '__main__':
    main()
