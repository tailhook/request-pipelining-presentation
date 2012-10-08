import copy
import msgpack
from zorro import zmq, zerogw, Hub
from zorro import redis
from zorro import mysql
from zorro import mongodb

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

class Service(zerogw.TreeService):

    def __init__(self, *args):
        super().__init__(*args)
        self.redis = redis.Redis(unixsock='tmp/redis.sock')
        self.mysql = mysql.Mysql(unixsock='tmp/mysql/socket')
        self.mongo = mongodb.Connection(socket_dir='tmp')['test']['counter']
        self.five_redises = [
            redis.Redis(unixsock='tmp/redis{}.sock'.format(i))
            for i in range(5)]

    @zerogw.public
    def hello_redis(self, uri):
        return str(self.redis.execute(b"INCR", b"redis_hello_counter"))

    @zerogw.public
    def hello5_redis5(self, uri):
        s = 0
        for r in self.five_redises:
            s += r.execute(b"INCR", b"redis_hello_counter")
        return str(s)

    @zerogw.public
    def count_redis(self, uri):
        num = int(uri.split('/')[-1])
        val = 0
        for i in range(num):
            val += self.redis.execute(b"INCR", b"redis_hello_counter")
        return str(val)

    @zerogw.public
    def bigger_redis(self, uri):
        self.redis.execute(b"SETNX", "user:1:lock")
        data = self.redis.execute(b"GET", b"user:1")
        if not data:
            data = copy.deepcopy(user_proto)
        else:
            data = msgpack.loads(data, encoding='utf-8')
        data['money'] += 100
        self.redis.execute(b"SET", b"user:1", msgpack.dumps(data))
        self.redis.execute(b"LPUSH", b"user:1:log",
            b"Added 100 money")
        self.redis.execute(b"LTRIM", 0, 99)
        self.redis.execute(b"DEL", "user:1:lock")
        return "MONEY: {}".format(data['money'])

    @zerogw.public
    def hello_mysql(self, uri):
        return str(self.mysql.execute(
            "UPDATE counter SET value = LAST_INSERT_ID(value + 1)").insert_id)

    @zerogw.public
    def hello_mongo(self, uri):
        self.mongo.update({'_id': 1}, {'$inc': {'counter': 1}}, upsert=True)
        return str(next(self.mongo.query({'_id': 1}))['counter'])

def main():
    svc = Service('uri')
    sock = zmq.rep_socket(svc)
    sock.connect("ipc://./tmp/zgw.sock")


if __name__ == '__main__':
    Hub().run(main)
