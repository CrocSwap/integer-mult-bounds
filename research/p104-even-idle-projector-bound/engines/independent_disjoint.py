"""Independent exact rational prefix-conjugate projector test."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal

CALLER = '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'


def basis(n):
    return [[Q(i == j) for i in range(n)] for j in range(n)]


def mix(a,b,c,d):
    return [c*x+d*y for x,y in zip(a,b,strict=True)]


def canonical(row,col):
    assert sum(x*y for x,y in zip(row,col,strict=True)) == 1
    pivot = next(x for x in row if x)
    return tuple(x/pivot for x in row),tuple(x*pivot for x in col)


def controls():
    R,C = basis(2),basis(2)
    original = canonical(R[0],C[0])
    R.reverse()
    C.reverse()
    assert canonical(R[1],C[1]) == original
    R[1] = mix(R[1],R[0],Q(1),Q(-2))
    C[0] = mix(C[0],C[1],Q(1),Q(2))
    assert canonical(R[1],C[1]) != original
    return ['swap_projector_relabel','signed_shear_changes_projector']


def sample(c,q):
    ty = c['types']['B']
    offset,n = ty['offset'],ty['roles']
    R,C = basis(n),basis(n)
    found = {}
    for i,e in enumerate(c['events']):
        if e[0]=='J':
            s,t,alpha,beta = e[3]
            s,t = s-offset,t-offset
            a,b,cc,d = Q(1),Q(alpha)*q,1/(2*q),Q(beta)
            assert a*d-b*cc == 1
            row_s,row_t = R[s],R[t]
            col_s,col_t = C[s],C[t]
            R[s],R[t] = mix(row_s,row_t,a,b),mix(row_s,row_t,cc,d)
            C[s],C[t] = mix(col_s,col_t,d,-cc),mix(col_s,col_t,-b,a)
            continue
        if e[0]!='B':
            continue
        _,op,r,*args = e
        r -= offset
        if op=='IDLE_ONE':
            assert args[0] and len(args[0]) == len(set(args[0]))
            found[i] = (r+offset,tuple(args[0]),canonical(R[r],C[r]))
            continue
        if op=='SWAP':
            s = args[0]-offset
            R[r],R[s] = R[s],R[r]
            C[r],C[s] = C[s],C[r]
        elif op in ('QUERY','ADD'):
            s = args[0]-offset
            k = q**args[1] if op=='QUERY' else Q(args[1])
            R[r] = mix(R[r],R[s],Q(1),k)
            C[s] = mix(C[s],C[r],Q(1),-k)
        else:
            assert op in ('LAMBDA','IDLE_ODD','SCALE')
            k = Q(1) if op=='LAMBDA' else q**args[1] if op=='IDLE_ODD' else Q(args[0])
            assert k
            R[r] = [x*k for x in R[r]]
            C[r] = [x/k for x in C[r]]
    assert len(found)==60
    for j,diag in enumerate(ty['diagonal']):
        want = q**diag[0]
        assert R[j] == [Q(k == j)*want for k in range(n)]
        for k in range(n):
            assert sum(a*b for a,b in zip(R[j],C[k],strict=True)) == (j==k)
    return found


def run(c):
    plus,minus = [sample(c,Q(q)) for q in (1,-1)]
    assert list(plus)==list(minus)
    checked = []
    for first,second in combinations(plus,2):
        r,a,x = plus[first]
        s,b,y = plus[second]
        assert (r,a)==minus[first][:2] and (s,b)==minus[second][:2]
        if not set(a).isdisjoint(b):
            continue
        p = x==y
        m = minus[first][2]==minus[second][2]
        checked.append({'clocks':[first,second],'roles':[r,s],'masks':[a,b],
                        'plus':p,'minus':m})
    assert len(checked)<=1770
    return {'caller_sha256':CALLER,'checked':len(checked),'controls':controls(),
            'both_survivors':sum(r['plus'] and r['minus'] for r in checked),
            'rows':checked}


if __name__ == '__main__':
    p = ArgumentParser(description=__doc__)
    p.add_argument('caller',type=Path)
    a = p.parse_args()
    signal(SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('exact prefix watchdog')))
    alarm(25)
    raw = a.caller.read_bytes()
    assert sha256(raw).hexdigest()==CALLER
    print(json.dumps(run(json.loads(raw)),indent=2,sort_keys=True))
    alarm(0)
