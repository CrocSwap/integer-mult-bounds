"""Exact pure prefix/suffix and unit pairing for the #7334 chart-207 split."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
WORD = '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a'
ADMISSION = 'c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13'
PROTECTED = {319,863,1355,1568}
CAP = 128


class Capped(Exception):
    pass


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check_time(deadline):
    if monotonic() >= deadline:
        raise Capped


def pinned(path, digest):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == digest, f'Changed input {path.name}')
    return raw


def unique(pairs):
    doc = dict(pairs)
    need(len(doc) == len(pairs), 'Duplicate receipt key')
    return doc


def read(raw):
    return loads(raw,object_pairs_hook=unique)


@cache
def rational(value):
    return Q(value)


def axpy(dst, src, factor):
    for j,v in src.items():
        value = dst.get(j,0) + factor*v
        if value:
            dst[j] = value
        else:
            dst.pop(j,None)


def dot(a,b):
    return sum(v*b.get(j,0) for j,v in a.items())


def compose(weights, rows):
    vector = {}
    for role, coefficient in weights.items():
        axpy(vector,rows[role],coefficient)
    return vector


def pure_kernel(rows, allowed, deadline):
    pivots, pure = {}, []
    for role,row in rows.items():
        check_time(deadline)
        exterior = {j:v for j,v in row.items() if j not in allowed}
        coeff = {role:Q(1)}
        while exterior:
            j = min(exterior)
            if j not in pivots:
                lead = exterior[j]
                pivots[j] = ({k:v/lead for k,v in exterior.items()},
                             {k:v/lead for k,v in coeff.items()})
                break
            other, op = pivots[j]
            factor = -exterior[j]
            axpy(exterior,other,factor)
            axpy(coeff,op,factor)
        else:
            projection = compose(coeff,rows)
            assert projection.keys() <= allowed
            pure.append((coeff,projection))
    assert len(pivots)+len(pure) == len(rows)
    return sorted(pivots), pure


def solve_bilinear(B,D,deadline):
    """Find x,y with xBy=1 and xDy=0, or prove no such rational pair."""
    n = len(B)
    def trial(x):
        bx,dx = compose(x,B),compose(x,D)
        if not bx:
            return None
        if not dx:
            j = min(bx)
            return x,{j:1/bx[j]}
        pivot = min(dx)
        for j in sorted(bx.keys() | dx.keys()):
            value = bx.get(j,0)*dx[pivot]-bx.get(pivot,0)*dx.get(j,0)
            if value:
                y = {j:dx[pivot]/value}
                if dx.get(j,0):
                    y[pivot] = -dx[j]/value
                assert dot(bx,y) == 1 and dot(dx,y) == 0
                return x,y
        return None
    for i in range(n):
        check_time(deadline)
        hit = trial({i:Q(1)})
        if hit:
            return hit
    # Each wedge coordinate is a homogeneous quadratic in x. Basis vectors
    # and pair sums determine all coefficients over Q.
    for i in range(n):
        check_time(deadline)
        for j in range(i+1,n):
            hit = trial({i:Q(1),j:Q(1)})
            if hit:
                return hit
    # All wedges vanish. Only xD=0 but xB!=0 can give a pair.
    _, kernel = pure_kernel(dict(enumerate(D)),set(),deadline)
    for x,_ in kernel:
        hit = trial(x)
        if hit:
            return hit
    return None


def paired(prefix,suffix,deadline):
    B,D = [],[]
    for a,c in prefix:
        check_time(deadline)
        dot_boundary = {j:v for j,(_,d) in enumerate(suffix) if (v:=dot(c,d))}
        dot_difference = {j:v for j,(b,_) in enumerate(suffix) if (v:=dot(a,b)-dot_boundary.get(j,0))}
        B.append(dot_boundary); D.append(dot_difference)
    hit = solve_bilinear(B,D,deadline)
    if hit is None:
        return None
    x,y = hit
    a,c = (compose(x,[pair[i] for pair in prefix]) for i in (0,1))
    b,d = (compose(y,[pair[i] for pair in suffix]) for i in (0,1))
    assert dot(a,b)==dot(c,d)==1
    return dict(a=a,b=b,c=c,d=d)


def initial_groups(word):
    n = word['public']
    main = set(word['live']) | {r+112 for r in word['live']}
    main.update(word['hosted']['X2']); main.update(word['hosted']['Y2'])
    cohort = {r for r in range(n) if r not in main and (word['initial'][r],word['final'][r])==(3,127)}
    return cohort-PROTECTED,cohort-PROTECTED


def prefix_rows(word, cuts, deadline):
    n = word['public']; rows = [{r:Q(1)} for r in range(n)]+[None]*word['owned_fields']
    charts = word['initial']+[None]*word['owned_fields']
    banks, seen = {}, 0
    try:
        for clock,event in enumerate(word['program']):
            if clock%64 == 0 or clock in cuts:
                check_time(deadline)
            if clock in cuts:
                banks[clock] = {r:rows[r].copy() for r in range(n) if charts[r]==207}
            if clock >= max(cuts):
                break
            op,dst,*args = event
            if op == 'MOVE':
                old,new,owned = args
                assert charts[dst] == old and owned==(dst>=n)
                charts[dst]=new
            elif op == 'INIT':
                assert dst>=n and rows[dst] is None
                rows[dst],charts[dst]={},args[0]
            elif op == 'CLEAR':
                assert dst>=n and charts[dst]==args[0]
                rows[dst]=charts[dst]=None
            elif op == 'SCALE':
                assert charts[dst]==args[1]
                rows[dst]={j:rational(args[0])*v for j,v in rows[dst].items()}
            else:
                src,q,chart=args
                assert charts[dst]==charts[src]==chart and src!=dst and op in {'ADD','COPY'}
                if op=='COPY':
                    assert dst>=n and not rows[dst], 'Dirty COPY'
                axpy(rows[dst],rows[src],rational(q))
            seen=clock+1
    except Capped:
        pass
    return banks,seen


def suffix_rows(word,banks,deadline):
    n=word['public']; cols=[{r:Q(1)} for r in range(n)]+[{} for _ in range(word['owned_fields'])]
    snapshots,seen={},0
    try:
        for clock in range(len(word['program']),min(banks)-1,-1):
            if clock%64==0 or clock in banks:
                check_time(deadline)
            if clock in banks:
                snapshots[clock]={r:cols[r].copy() for r in banks[clock]}
            if clock==min(banks):
                break
            op,dst,*args=word['program'][clock-1]
            if op in {'ADD','COPY'}:
                src,q,_=args
                axpy(cols[src],cols[dst],rational(q))
                if op=='COPY':
                    cols[dst]={}
            elif op=='SCALE':
                cols[dst]={j:rational(args[0])*v for j,v in cols[dst].items()}
            elif op in {'INIT','CLEAR'}:
                cols[dst]={}
            else:
                assert op=='MOVE'
            seen+=1
    except Capped:
        pass
    return snapshots,seen


def geometry_keys(geometry):
    if 'representative_keys' in geometry:
        raw=geometry['representative_keys']
    elif 'keys' in geometry:
        raw=geometry['keys']
    else:
        raw=[(row['cut'],row['chart'],pivot) for row in geometry['segments'] for pivot in row['pivots']]
    result=[tuple(row) if not isinstance(row,dict) else (row['cut'],row['chart'],row['pivot']) for row in raw]
    need(len(result)==len(set(result)) and all(len(row)==3 and row[1]==207 and 44588<=row[0]<=44628 for row in result),'Wrong geometry key inventory')
    return result


def audit(word,geometry,deadline):
    all_keys=geometry_keys(geometry)
    if not all_keys:
        return dict(status='empty_geometry',selected=0,decisions=[],unresolved=[])
    keys=all_keys[:CAP]
    cohort,pivots=initial_groups(word)
    if 'endpoint_cohort' in geometry:
        assert sorted(cohort)==geometry['endpoint_cohort']
    overflow=[tuple(key) for key in geometry.get('unvisited_keys',())]
    assert len(overflow)==len(set(overflow)) and not set(overflow).intersection(all_keys)
    bank_plan=defaultdict(list)
    for cut,chart,pivot in keys:
        need(pivot in pivots,'Protected or non-helper pivot')
        bank_plan[cut].append(pivot)
    banks,forward=prefix_rows(word,bank_plan,deadline)
    decisions,opens={}, {}
    try:
        for cut,bank in banks.items():
            need(set(bank_plan[cut])<=bank.keys(),'Pivot absent from literal chart bank')
            exterior,pure=pure_kernel(bank,cohort,deadline)
            if any(c for _,c in pure):
                opens[cut]=(exterior,pure)
            else:
                decisions[cut]=dict(status='no_nonzero_pure_prefix',public_bank=list(bank),
                                    prefix_exterior_pivots=exterior,prefix_nullity=len(pure))
    except Capped:
        pass
    backward=0
    if opens:
        snapshots,backward=suffix_rows(word,{c:banks[c] for c in opens},deadline)
        try:
            for cut,bank in snapshots.items():
                exterior,pure=pure_kernel(bank,cohort,deadline)
                pre_rank,pre=opens[cut]
                row=dict(public_bank=list(bank),prefix_exterior_pivots=pre_rank,
                         suffix_exterior_pivots=exterior,prefix_nullity=len(pre),suffix_nullity=len(pure))
                if not any(d for _,d in pure):
                    decisions[cut]=row|dict(status='no_nonzero_pure_suffix')
                    continue
                witness=paired(pre,pure,deadline)
                if witness is None:
                    decisions[cut]=row|dict(status='no_unit_pairing')
                    continue
                assert compose(witness['a'],banks[cut])==witness['c']
                assert compose(witness['b'],bank)==witness['d']
                decisions[cut]=row|dict(status='exact_support_only',witness={k:{j:str(v) for j,v in value.items()} for k,value in witness.items()})
        except Capped:
            pass
    rows=[dict(key=key,**decisions[key[0]]) for key in keys if key[0] in decisions]
    unresolved=[key for key in all_keys if key[0] not in decisions or key not in keys] + overflow
    return dict(status='CAPPED' if unresolved else 'EXHAUSTED',selected=len(keys),
                eligible_cohort=sorted(cohort),prefix_events=forward,suffix_events=backward,
                decisions=rows,unresolved=unresolved,support_only=[row['key'] for row in rows if row['status']=='exact_support_only'])


def controls():
    inf=float('inf')
    _,a=pure_kernel({4:{0:Q(1),2:Q(1)},5:{2:Q(1)}},{0},inf)
    _,b=pure_kernel({4:{0:Q(1)},5:{3:Q(1)}},{0},inf)
    hit=paired(a,b,inf)
    assert hit and hit['a'][4] == -hit['a'][5] != 0
    assert dot(hit['a'],hit['b']) == dot(hit['c'],hit['d']) == 1
    _,wrong=pure_kernel({4:{0:Q(1),3:Q(1)},5:{3:Q(1)}},{0},inf)
    assert paired(a,wrong,inf) is None
    assert solve_bilinear([{0:Q(1)},{1:Q(1)}],[{0:Q(1)},{1:Q(2)}],inf)[0]=={0:Q(1),1:Q(1)}
    assert solve_bilinear([{0:Q(1)},{0:Q(2)}],[{0:Q(1)},{0:Q(1)}],inf) is not None
    return ['signed_unit_pair','unequal_pairing_rejected','quadratic_cross_term','left_kernel_D']


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--controls-only',action='store_true')
    for key in ('word','price','geometry','admission'):
        p.add_argument('--'+key,type=Path)
    p.add_argument('--price-sha'); p.add_argument('--geometry-sha')
    a=p.parse_args()
    assert __debug__
    checks=controls()
    if a.controls_only:
        print(dumps(dict(controls=checks),indent=2,sort_keys=True)); return
    need(all((a.word,a.price,a.geometry,a.admission,a.price_sha,a.geometry_sha)),'Sealed geometry and price are required')
    price=read(pinned(a.price,a.price_sha)); geom=read(pinned(a.geometry,a.geometry_sha))
    admission=read(pinned(a.admission,ADMISSION))
    assert price['head']==admission['head']==HEAD and admission['exit']==0
    assert price['productive_delta']=={'1':17,'8':17,'9':-17} and not price['paid_delta']
    assert admission['inputs']['WORD.json.gz']==WORD
    if 'price_sha256' in geom:
        assert geom['price_sha256']==a.price_sha
    if 'word_sha256' in geom:
        assert geom['word_sha256']==WORD
    keys=geometry_keys(geom)
    if keys:
        def watchdog(*_):
            raise TimeoutError('hard support watchdog')
        signal(SIGALRM,watchdog)
        alarm(35)
        try:
            deadline=monotonic()+32
            result=audit(read(decompress(pinned(a.word,WORD))),geom,deadline)
        finally:
            alarm(0)
    else:
        result=dict(status='empty_geometry',selected=0,decisions=[],unresolved=[])
    result.update(head=HEAD,word_sha256=WORD,admission_sha256=ADMISSION,price_sha256=a.price_sha,
                  geometry_sha256=a.geometry_sha,cap=CAP,seconds_cap=35,controls=checks,
                  unvisited_credit_upper=price['one_edit_optimistic_credit'][1])
    print(dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
