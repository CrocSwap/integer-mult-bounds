"""Finite regression controls for the informal all-input lane theorem."""
import itertools, json

def need(ok, message):
    if not ok:
        raise ValueError(message)

def encode(xs, b, r):
    return sum((x+b)*r**j for j,x in enumerate(xs))

def main():
    checks = 0
    for b in (6,12):
        cmax = 3
        s = (2*(cmax+2)*b).bit_length()
        r = 1 << s
        domain = tuple(range(-b,b+1))
        for k in (1,2,3):
            w = k*s
            mask = (1 << w)-1
            rep = sum(r**j for j in range(k))
            vectors = itertools.product(domain,repeat=k)
            for x in vectors:
                e = encode(x,b,r)
                neg = max(2*b*rep-e,0)&mask
                need(neg==encode(tuple(-v for v in x),b,r),'neg')
                checks += 1
                for c in (0,1,2,3):
                    if all(abs(c*v)<=b for v in x):
                        tmp=(c*e)&mask
                        result=max(tmp-(c-1)*b*rep,0)&mask if c else b*rep
                        need(result==encode(tuple(c*v for v in x),b,r),'scalar')
                        checks += 1
                for d in (1,2,3,6):
                    if all(v%d==0 for v in x):
                        result=(e//d+(d-1)*(b//d)*rep)&mask
                        need(result==encode(tuple(v//d for v in x),b,r),'division')
                        checks += 1
                # Independent lanes and mixed signs, with a bounded subset of y.
                for y in (tuple(0 for _ in x),tuple(-v for v in x),x,
                          tuple((-1)**j for j in range(k))):
                    ey=encode(y,b,r)
                    if all(abs(a+z)<=b for a,z in zip(x,y)):
                        result=max(((e+ey)&mask)-b*rep,0)&mask
                        need(result==encode(tuple(a+z for a,z in zip(x,y)),b,r),'add')
                        checks += 1
                    if all(abs(a-z)<=b for a,z in zip(x,y)):
                        result=max(((e+b*rep)&mask)-ey,0)&mask
                        need(result==encode(tuple(a-z for a,z in zip(x,y)),b,r),'sub')
                        checks += 1
    print(json.dumps({'status':'PASS_FINITE_REGRESSION_ONLY',
                      'exact_checks':checks,'basis':'w-bit modular multiply/add, monus, integer division',
                      'proof_scope':'informal universal argument in BIASED-LANE-COMPILER.md'},indent=2))

if __name__=='__main__':
    main()
