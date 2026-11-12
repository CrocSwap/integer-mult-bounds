"""Exact rank-three certificates for every first/last-stage triple."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
N, CASES, SECONDS = 36, 140, 40


def dot(a,b):
    return sum(x*y for x,y in zip(a,b,strict=True) if x and y)


def add(a,b,c):
    return [x+c*y for x,y in zip(a,b,strict=True)] if c else a[:]


def stop(*_):
    raise TimeoutError('40-second triple rank cap')


def rank_indices(vectors):
    rows, pivots, picked = [], [], []
    for i,v in enumerate(vectors):
        w = v[:]
        for j,row in zip(pivots,rows,strict=True):
            w = add(w,row,-w[j])
        j = next((j for j,x in enumerate(w) if x),None)
        if j is not None:
            rows.append([x/w[j] for x in w])
            pivots.append(j)
            picked.append(i)
    return picked


def det3(m):
    a,b,c = m
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])


def verify_pins():
    pins = {}
    for line in (ROOT/'PINS').read_text().splitlines():
        expected,path = line.split()
        assert path not in pins and sha256((ROOT/path).read_bytes()).hexdigest()==expected
        pins[path] = expected
    return pins


def json_file(path):
    return loads((ROOT/path).read_bytes())


def transport(factors, chosen, idx):
    u,v = factors[idx]
    for j in range(idx+1,chosen[-1]):
        if j in chosen:
            continue
        x,y = factors[j]
        u,v = add(u,x,dot(y,u)),add(v,y,-dot(v,x))
    assert not dot(u,v)
    return u,v


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    pins = verify_pins()
    prior = json_file('inputs/R194-RESULT.json')
    rank_predecessor = json_file('inputs/R193-RESULT.json')
    assert (prior['head'],prior['caller'],prior['factor_count'])==(HEAD,CALLER,38)
    assert (rank_predecessor['head'],rank_predecessor['caller'])==(HEAD,CALLER)
    f = run_path(str(ROOT/'inputs/forward.py'))
    r = run_path(str(ROOT/'inputs/reverse.py'))
    unit,apply,cv = f['unit'],f['apply'],r['covector']
    tape = json_file('inputs/CALLER.json')['events']
    assert len(tape)==4783
    factors,labels = [],[]
    for clock,event in enumerate(tape):
        if event[0]=='J':
            _,stage,(u,v,x,y),_ = event
            legs = ((v,u,1),(x,y,-1))
        elif event[:2]==['A','QUERY']:
            _,_,v,u,exp = event
            assert exp==-1
            stage,legs = 0,((v,u,1),)
        else:
            continue
        for leg,(d,s,sign) in enumerate(legs):
            before = tape[:clock]
            out = [2*sign*x for x in apply(before,unit(d),-1,inverse=True)]
            row = cv(before,unit(s),-1)
            assert not dot(row,out)
            factors.append((out,row))
            labels.append([clock,stage,leg,d,s,sign])
    assert labels==prior['factor_labels']
    for i in range(N):
        e = unit(i)
        for u,v in factors:
            e = add(e,u,dot(v,e))
        assert e==[-x for x in unit(i)]
    triples = [t for t in combinations(range(38),3) if min(t)<2 and max(t)>=36]
    assert len(triples)==CASES
    cases,counts = [],Counter()
    for triple in triples:
        shifted = [transport(factors,triple,i) for i in triple]
        columns = [u for u,_ in shifted]
        rows = []
        for u,v in shifted:
            w = v[:]
            for x,y in zip(columns,rows):
                w = add(w,y,dot(v,x))
            rows.append(w)
        ri,ci = rank_indices(list(zip(*columns,strict=True))),rank_indices(list(zip(*rows,strict=True)))
        case = {'triple':triple,'labels':[labels[i] for i in triple]}
        if len(ri)==len(ci)==3:
            minor = [[sum(columns[k][i]*rows[k][j] for k in range(3)) for j in ci] for i in ri]
            det = det3(minor)
            assert det
            case.update(rank=3,minor={'rows':ri,'columns':ci,'matrix':minor,'determinant':det})
        else:
            delta = [[sum(columns[k][i]*rows[k][j] for k in range(3)) for j in range(N)] for i in range(N)]
            rank = len(rank_indices(delta))
            assert rank<=2
            case.update(rank=rank,transported_factors=shifted,delta_rows=delta)
        counts[case['rank']]+=1
        cases.append(case)
    alarm(0)
    print(dumps({'head':HEAD,'caller':CALLER,'pins':pins,'factor_count':len(factors),'factor_labels':labels,
                 'case_cap':CASES,'runner_cap_seconds':SECONDS,'counts':counts,'cases':cases,
                 'survivors':[c['triple'] for c in cases if c['rank']<=2]},
                default=str,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
