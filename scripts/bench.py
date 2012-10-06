#!/usr/bin/python
import subprocess
import decimal
import csv
import time
import os

REQUESTS = 100000
USERS = ([]
    + list(range(1,   20,   1))
    + list(range(20,  100,  5))
    + list(range(100, 1001, 50))
    )

RETRIES = 3
#REQUESTS = 10000
#USERS = range(1, 100, 10)

def run_test(example, db, kind, instances, count='', force=False):
    if count:
        fn = '{kind}_{example}_{db}_{instances}_{count}'.format(
            kind=kind, example=example, db=db,
            instances=instances, count=count)
    else:
        fn = '{kind}_{example}_{db}_{instances}'.format(
            kind=kind, example=example, db=db, instances=instances)
    outfn = 'results/' + fn + '.csv'
    if os.path.exists(outfn):
        return
    log = open('tmp/' + fn + '.log', 'wb')
    out = open(outfn + '.tmp', 'wt')
    file = csv.writer(out)
    file.writerow(['users', 'rps', 'min', 'avg', 'sd', 'median', 'max'])

    print("Running", example, kind, db, "on", instances, "processes", '({})'.format(fn))

    for users in USERS:
        row = None
        for i in range(0, RETRIES):
            tm = time.time()
            data, _ = subprocess.Popen(['bossrun',
                '--config=config/run_{}.yaml'.format(db),
                '-Dinstances={}'.format(instances),
                '-Dconcurrent={}'.format(users),
                '-Dnum_requests={}'.format(REQUESTS),
                '-Dexample={}'.format(example),
                '-Dkind={}'.format(kind),
                '-Dcount={}'.format(count),
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
    os.rename(outfn + '.tmp', outfn)

run_test('hello', 'mysql', 'sync', 1)
run_test('hello', 'mysql', 'sync', 2)
run_test('hello', 'mysql', 'sync', 5)
run_test('hello', 'mysql', 'sync', 10)

run_test('hello', 'mysql', 'async', 1)
run_test('hello', 'mysql', 'async', 2)

run_test('hello', 'mongo', 'sync', 1)
run_test('hello', 'mongo', 'sync', 2)
run_test('hello', 'mongo', 'sync', 5)
run_test('hello', 'mongo', 'sync', 10)

run_test('hello', 'mongo', 'async', 1)
run_test('hello', 'mongo', 'async', 2)

run_test('hello', 'redis', 'async', 1)
run_test('hello', 'redis', 'async', 2)

run_test('bigger', 'redis', 'async', 1)
run_test('bigger', 'redis', 'async', 2)

run_test('hello', 'redis', 'sync', 1)
run_test('hello', 'redis', 'sync', 2)
run_test('hello', 'redis', 'sync', 5)
run_test('hello', 'redis', 'sync', 10)

run_test('bigger', 'redis', 'sync', 1)
run_test('bigger', 'redis', 'sync', 2)

run_test('count', 'redis', 'async', 1, 10)
run_test('count', 'redis', 'async', 1, 20)
run_test('count', 'redis', 'async', 1, 30)

run_test('count', 'redis', 'sync', 1, 10)
run_test('count', 'redis', 'sync', 1, 20)
run_test('count', 'redis', 'sync', 1, 30)

run_test('count', 'redis', 'async', 2, 10)
run_test('count', 'redis', 'async', 2, 20)
run_test('count', 'redis', 'async', 2, 30)

run_test('count', 'redis', 'sync', 2, 10)
run_test('count', 'redis', 'sync', 2, 20)
run_test('count', 'redis', 'sync', 2, 30)


