"""Exact rational Type A provider phase-difference rank control."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import runpy
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
CALLER = 'round30/complex/source/inputs/CALLER.json'
MODEL = 'round45/lead/screen.py'
PRICE = 'round45/lead/run/PRICE.json'
SUPPORT = 'round45/lead/run/SUPPORT.json'
PINS = {
    CALLER: '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    MODEL: 'a2b373d9989e644220d5d7fa61ff2c395e6b30edc651da7a8026f229d87828a4',
    PRICE: '8c7862be17c0ba549d4135af3f0e8dfb6b7dcec08bb8a91895194978280097d6',
    SUPPORT: '1ba39fa79654c1ae887b2e2a2b3c1394d87a15e1bffa7a3e6960c4f29280311c',
    'round45/lead/references/check_odd_caller_exact_grid.py': 'abd5a5fd011b71e5b382cbc058855594d4f2fe7b049f375506675c0303180f54',
}


def decode(raw):
    def unique(pairs):
        data = dict(pairs)
        assert len(data) == len(pairs), 'duplicate JSON key'
        return data
    return json.loads(raw, object_pairs_hook=unique)


def save(out, name, data):
    tmp = out / (name + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
    tmp.replace(out / name)


def det(matrix):
    if not matrix:
        return Q(1)
    top, *rest = matrix
    return sum((-1)**j * v * det([r[:j]+r[j+1:] for r in rest])
               for j,v in enumerate(top) if v)


def exact_rank(matrix):
    """Eliminate complete rational rows and recover an original nonzero minor."""
    pivots = []
    for i, original in enumerate(matrix):
        row = original.copy()
        for _,j,pivot in pivots:
            if row[j]:
                scale = row[j]
                row = [v-scale*b for v,b in zip(row,pivot,strict=True)]
        j = next((k for k,v in enumerate(row) if v), None)
        if j is not None:
            pivots.append((i,j,[v/row[j] for v in row]))
    ri = [i for i,_,_ in pivots]
    ci = [j for _,j,_ in pivots]
    minor = det([[matrix[i][j] for j in ci] for i in ri])
    assert minor
    return len(pivots), ri, ci, minor


def phase_difference(model, n, plus, minus, left, right):
    cols = []
    for j in range(n):
        vector = model['unit'](n,j)
        a = model['transform'](vector.copy(),plus)
        b = model['transform'](vector,minus)
        cols.append([b[i]-a[i]-2*left[i]*right[j] for i in range(n)])
    return [list(r) for r in zip(*cols,strict=True)]


def controls():
    matrix = [[Q(0),Q(0),Q(1,3)],[Q(0),Q(2,5),Q(0)],[Q(65537),Q(0),Q(0)]]
    rank, ri, ci, minor = exact_rank(matrix)
    assert rank == 3 and ri == [0,1,2] and ci == [2,1,0] and minor == Q(131074,15)
    matrix[2] = [Q(0),Q(4,5),Q(-1,3)]
    assert exact_rank(matrix)[0] == 2
    assert exact_rank([[Q(0),Q(0)],[Q(0),Q(0)]]) == (0,[],[],Q(1))
    return ['independent_permuted_pivots_and_exact_minor', 'dependent_row_rank_two',
            'zero_matrix_rank_zero', 'exact_rank_three_with_prime_divisible_minor']


def run(roots, out, deadline):
    data = {}
    for key, pin in PINS.items():
        root, rel = key.split('/',1)
        raw = (roots[root]/rel).read_bytes()
        assert sha256(raw).hexdigest() == pin, ('changed input', key)
        data[key] = raw
    model = runpy.run_path(str(roots['round45']/'lead/screen.py'))
    assert model['HEAD'] == HEAD
    caller, price, support = [decode(data[k]) for k in (CALLER,PRICE,SUPPORT)]
    assert price['head'] == support['head'] == HEAD
    assert support['price_sha256'] == PINS[PRICE] and support['checked'] == 68
    assert not support['unvisited']
    a = caller['types']['A']
    n = a['roles']
    assert n == 36 and a['offset'] == 0
    queries = [(t,e[2:]) for t,e in enumerate(caller['events']) if e[:2]==['A','QUERY']]
    stages = [(t,e[1]) for t,e in enumerate(caller['events']) if e[0]=='J']
    stock = [(p,j) for (p,_),(j,_) in product(queries,stages)]
    assert len(stock)==68 and stock == [(r['query_clock'],r['j_clock']) for r in support['rows']]
    assert stock == [(r['query_clock'],r['j_clock']) for r in price['alternatives']]
    blocks = {q:model['elementary'](caller,q) for q in (-1,1)}
    at = {q:dict(b) for q,b in blocks.items()}
    zero = [Q(0)]*n
    for j,_ in stages:
        assert exact_rank(phase_difference(model,n,at[1][j],at[-1][j],zero,zero))[0] == 2
    records = []
    for (p,(d,s,exponent)),(j,stage) in product(queries,stages):
        if monotonic() >= deadline:
            break
        assert exponent % 2
        middle = tuple(op for t,part in blocks[-1] if min(p,j)<t<max(p,j) for op in part)
        plus,minus = at[1][j],at[-1][j]
        left,right = model['correction'](n,d,s,minus,middle,p<j)
        matrix = phase_difference(model,n,plus,minus,left,right)
        rank, ri, ci, minor = exact_rank(matrix)
        assert rank <= 3
        records.append(dict(query_clock=p,j_clock=j,stage=stage,rank=rank,
                            pivot_rows=ri,pivot_columns=ci,exact_minor=str(minor),
                            minor_entries=[[str(matrix[i][k]) for k in ci] for i in ri],
                            update_column={i:str(x) for i,x in enumerate(left) if x},
                            update_row={i:str(x) for i,x in enumerate(right) if x},
                            admissible_necessary_rank=rank<=2))
    pending = stock[len(records):]
    save(out,'RESULT.json',dict(head=HEAD,pins=PINS,controls=controls(),
          body_specialization=1,q_specializations=[1,-1],old_provider_phase_difference_rank=2,
          checked=len(records),unvisited=pending,counts=dict(Counter(r['rank'] for r in records)),
          admissible_cases=[[r['query_clock'],r['j_clock']] for r in records if r['rank']<=2],
          records=records,gate='Necessary exact phase rank under common invertible q-even left/right adapters.'))


def main():
    p=ArgumentParser()
    for name in ('round30','round45','out'):
        p.add_argument(name,type=Path,nargs='?')
    p.add_argument('--seconds',type=int,default=30,choices=range(2,31),metavar='2..30')
    p.add_argument('--controls-only',action='store_true')
    a=p.parse_args()
    if a.controls_only:
        print(json.dumps(controls()))
        return
    if None in (a.round30,a.round45,a.out):
        p.error('Round 30 and Round 45 roots and a fresh output are required')
    a.out.mkdir()
    def cap(*_):
        raise TimeoutError('hard runner deadline')
    signal(SIGALRM,cap)
    alarm(a.seconds)
    try:
        run({'round30':a.round30,'round45':a.round45},a.out,monotonic()+a.seconds-1)
    except TimeoutError:
        save(a.out,'TIMEOUT.json',dict(head=HEAD,unverified=68,status='hard_timeout',seconds_cap=a.seconds))
        raise SystemExit(2)
    finally:
        alarm(0)


if __name__=='__main__':
    main()
