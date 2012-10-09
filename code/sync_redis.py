import zmq
import socket
import hiredis
import copy
import msgpack

user_proto = {
    'name': 'user1',
    'firstname': 'John',
    'lastname': 'Smith',
    'country': 'Ukraine',
    'city': 'Lviv',
    'birthdate': '12-03-1965',
    'email': 'john.smith@example.com',
    'password': 'deadbeefdeadbeefdeadbeefdeadbeef',
    'is_staff': 0,
    'is_active': 1,
    'is_superuser': 2,
    'last_login': '2012-07-01T21:24:32',
    'date_joined': '2012-07-01T21:24:32',
    'money': 0,
}


class Service:

    def __init__(self):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect('tmp/redis.sock')
        self.hiredis = hiredis.Reader()

    def hello_redis(self, uri):
        return str(self.redis_execute(b"INCR", b"redis_hello_counter"))

    def slow_redis(self, uri):
        return str(sum(map(int, (self.redis_execute(b"SINTER", b"million", b"primes", b"shift")))))

    def count_redis(self, uri):
        num = int(uri.split('/')[-1])
        val = 0
        for i in range(num):
            val += self.redis_execute(b"INCR", b"redis_hello_counter")
        return str(val)

    def redis_execute(self, *args):
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
        self.socket.sendall(buf)
        while True:
            chunk = self.socket.recv(4096)
            if not chunk:
                raise RuntimeError('Connection closed')
            self.hiredis.feed(chunk)
            data = self.hiredis.gets()
            if data is not False:
                break
        return data

    def bigger_redis(self, uri):
        self.redis_execute(b"SETNX", "user:1:lock")
        data = self.redis_execute(b"GET", "user:1")
        if not data:
            data = copy.deepcopy(user_proto)
        else:
            data = msgpack.loads(data, encoding='utf-8')
        data['money'] += 100
        self.redis_execute(b"SET", "user:1", msgpack.dumps(data))
        self.redis_execute(b"LPUSH", "user:1:log",
            b"Added 100 money")
        self.redis_execute(b"LTRIM", 0, 99)
        self.redis_execute(b"DEL", "user:1:lock")
        return "MONEY: {}".format(data['money'])


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
