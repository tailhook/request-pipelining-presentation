def postponed_sieve():  # postponed sieve, by Will Ness
    yield 2; yield 3; yield 5; yield 7;
    D = {}
    c = 9
    ps = (p for p in postponed_sieve())
    p = next(ps) and next(ps)               # 3
    q = p*p                                 # 9
    while True:
        if c not in D:
            if c < q: yield c
            else:
                add(D,c + 2*p,2*p)
                p=next(ps)
                q=p*p
        else:
            s = D.pop(c)
            add(D,c + s,s)
        c += 2

def add(D,x,s):
    while x in D: x += s
    D[x] = s

for i in postponed_sieve():
    print(i)
