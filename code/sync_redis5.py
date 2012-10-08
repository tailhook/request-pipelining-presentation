import zmq
import socket
import hiredis

class Service:

    def __init__(self):
        self.sockets = []
        self.hiredises = []
        for i in range(5):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect('tmp/redis{}.sock'.format(i))
            self.sockets.append(sock)
            self.hiredises.append(hiredis.Reader())

    def hello5_redis5(self, uri):
        s = 0
        for i in range(5):
            s += self.redis_execute(i, b"INCR", b"redis_hello_counter")
        return str(s)

    def redis_execute(self, i, *args):
        socket = self.sockets[i]
        hiredis = self.hiredises[i]
        buf = bytearray()
        bufadd = buf.extend
        bufadd(b'*')
        bufadd(str(len(args)).encode('ascii'))
        bufadd(b'\r\n')
        for i in args:
            if not isinstance(i, bytes):
                if not isinstance(i, str):
                    i = str(i)
                i = i.encode('utf-8')
            bufadd(b'$')
            bufadd(str(len(i)).encode('ascii'))
            bufadd(b'\r\n')
            bufadd(i)
            bufadd(b'\r\n')
        socket.sendall(buf)
        while True:
            chunk = socket.recv(4096)
            if not chunk:
                raise RuntimeError('Connection closed')
            hiredis.feed(chunk)
            data = hiredis.gets()
            if data is not False:
                break
        return data


def main():
    svc = Service()
    ctx = zmq.Context()
    sock = ctx.socket(zmq.REP)
    sock.connect("ipc://./tmp/zgw.sock")
    while True:
        uri, = sock.recv_multipart()
        uri = uri.decode('ascii')
        mname = uri.strip('/_').split('/')[0]
        try:
            meth = getattr(svc, mname)
        except AttributeError:
            sock.send_multipart([b'404 Not Found', b'<h1>404 Not Found</h1>'])
        else:
            res = meth(uri)
            sock.send_multipart([res.encode('ascii')])


if __name__ == '__main__':
    main()
