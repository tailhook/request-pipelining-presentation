#!/usr/bin/python
import subprocess
import decimal
import csv
import time

REQUESTS = 100000
USERS = (
    list(range(1,   20,   1)) +
    list(range(20,  100,  5)) +
    list(range(100, 1000, 50)
    )

RETRIES = 3
REQUESTS = 10000
USERS = range(1, 100, 10)

def run_test(config, page, instances):
    fn = '{page}_p{instances}'.format(page=page, instances=instances)
    log = open('tmp/' + fn + '.log', 'wb')
    out = open('results/' + fn + '.csv', 'wt')
    file = csv.writer(out)
    file.writerow(['users', 'rps', 'min', 'avg', 'sd', 'median', 'max'])

    print("Running", page, "on", instances, "processes", '({})'.format(fn))

    for users in USERS:
        row = None
        for i in range(0, RETRIES):
            tm = time.time()
            data, _ = subprocess.Popen(['bossrun',
                '--config=config/{}.yaml'.format(config),
                '-Dinstances={}'.format(instances),
                '-Dconcurrent={}'.format(users),
                '-Dnum_requests={}'.format(REQUESTS),
                ], stdout=subprocess.PIPE, stderr=log).communicate()
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
            print('---> {}-{}. {rps}, {min}, {avg}, {sd}, '
                  '{median}, {max} in {:.2f}s'
                  .format(users, i, tm, **info))
        file.writerow([users, info['rps'], info['min'], info['avg'],
                              info['sd'], info['median'], info['max']])

    out.close()


run_test('run_mysql', 'hello_mysql', 1)
run_test('run_mysql', 'hello_mysql', 2)
run_test('run_mysql', 'hello_mysql', 3)

