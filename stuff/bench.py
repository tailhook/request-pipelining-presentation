#!/usr/bin/python
import subprocess
import decimal
import csv
import time

#REQUESTS = 1000000
#USERS = list(range(1, 100)) + list(range(100, 1000, 10))
RETRIES = 3
REQUESTS = 10000
USERS = range(1, 100, 10)
PAGE = 'hello_redis'
COMMAND_LINE = ('exec ab -k -n {requests} -c {users} '
                'http://localhost:8000/{page}')

out = open('{page}_p1.csv'.format(page=PAGE), 'wt')
file = csv.writer(out)
file.writerow(['users', 'rps', 'min', 'avg', 'sd', 'median', 'max'])

for users in USERS:
    row = None
    for i in range(0, RETRIES):
        tm = time.time()
        data, _ = subprocess.Popen(COMMAND_LINE.format(
            requests=REQUESTS,
            users=users,
            page=PAGE,
            ),
            shell=True,
            stdout=subprocess.PIPE,
            ).communicate()
        data = data.decode('ascii')

        info = {}
        for line in data.splitlines():
            if line.startswith('Requests per second:'):
                info['rps'] = decimal.Decimal(line.split()[3])
            elif line.startswith('Total:'):
                pieces = map(decimal.Decimal, line.split()[1:])
                info['min'], info['avg'], info['sd'], \
                    info['median'], info['max'] = pieces
        if not row or info['rps'] > row['rps']:
            row = info
        tm = time.time() - tm
        print('{}-{}. {rps}, {min}, {avg}, {sd}, {median}, {max} in {:.2f}s'
            .format(users, i, tm, **info))
    file.writerow([users, info['rps'], info['min'], info['avg'],
                          info['sd'], info['median'], info['max']])



