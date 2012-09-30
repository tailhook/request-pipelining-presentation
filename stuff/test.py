from zorro import zmq, zerogw, Hub
from zorro import redis
from zorro import mysql
from zorro import mongodb

class Service(zerogw.TreeService):

    def __init__(self, *args):
        super().__init__(*args)
        self.redis = redis.Redis()
        self.mysql = mysql.Mysql(unixsock='tmp/mysql/socket')
        self.mongo = mongodb.Connection()['test']['counter']

    @zerogw.public
    def hello_redis(self, uri):
        return str(self.redis.execute(b"INCR", b"redis_light_counter"))

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
