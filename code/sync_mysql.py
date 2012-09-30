import zmq
import oursql


class Service:

    def __init__(self):
        self.mysql = oursql.Connection(unix_socket='tmp/mysql/socket',
                                       db='test')

    def hello_mysql(self):
        cursor = self.mysql.cursor()
        cursor.execute("UPDATE counter SET value = LAST_INSERT_ID(value + 1)")
        return str(cursor.lastrowid)


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
