import zmq
import pymongo


class Service:

    def __init__(self):
        self.mongo = pymongo.Connection()['test']['counter']

    def hello_mongo(self):
        self.mongo.update({'_id': 1}, {'$inc': {'counter': 1}}, upsert=True)
        return str(self.mongo.find_one({'_id': 1})['counter'])


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