"""Directed signed invoice and paired rank-reduction ceilings."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

TARGET = F(10018846261809, 2500000000000000)
CLAIMS = F('0.003645372367832'), F('0.003645473221716')
GRID = 10**48
PINS = {
    'old/inputs/native/WORD.json.gz': '75061d1e4b354e4cf36b690f30ddb2b257ed2f4e86509f87e17bb0f63eca126f',
    'old/inputs/native/RESULT.json': '75f34132b5b12b1a92f13b7a7c47ea3857f1955403090ae06b38dd9cf18aeb49',
    'old/inputs/caller/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'peer/WORD.json.gz': '66bc395b599bc0b805c5061bbbd124e2027ad86645c07abe40d0b472fa1a7a2b',
    'peer/RESULT.json': 'acd6ef312fc1d1b8a94919b345667fb17a8a38939db17976ba6a21c7d4de9eb9',
}


def load(old, peer):
    roots = {'old':old, 'peer':peer}
    out = {}
    for name, digest in PINS.items():
        label, path = name.split('/', 1)
        raw = (roots[label] / path).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f'Pinned SHA-256 mismatch: {name}')
        out[name] = json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
    return list(out.values())


def invoice(word, caller):
    ranks = list(map(len, word['frames']))
    main = set(word['live']) | {i+112 for i in word['live']} | set(word['hosted']['X2'] + word['hosted']['Y2'])
    assert len(main) == 400 and word['public'] == 1501 and len(word['program']) == 76444
    paid, target = Counter(), Counter()
    for op, role, *args in word['program']:
        if op == 'MOVE':
            src, dst, owned = args
            assert owned == (role >= word['public']) and ranks[src] != ranks[dst]
            paid[abs(ranks[src]-ranks[dst])] += 1
    for role, (src, dst) in enumerate(zip(word['initial'], word['final'], strict=True)):
        if role not in main:
            assert ranks[dst] > ranks[src]
            target[ranks[dst]-ranks[src]] += 1
    stages = [event[1] for event in caller['events'] if event[0] == 'J']
    assert stages == list(range(1, 18))
    copies = len(stages)
    P = Counter({rank:n*copies for rank,n in paid.items()})
    T = Counter({rank:n*copies for rank,n in target.items()})
    for spec in caller['types'].values():
        for sign, offset, *bits in spec['diagonal']:
            assert sign == -1 and offset == 0 and len(bits) == copies and set(bits) <= {0, 1}
            T[1+8*sum(bits)] += len(spec['ports'])
    for kind, op, *args in (event for event in caller['events'] if event[0] != 'J'):
        n = len(caller['types'][kind]['ports'])
        if op == 'QUERY':
            P[1] += n
        elif op in ('IDLE_ONE','IDLE_ODD'):
            P[8*len(args[1])+int(op=='IDLE_ODD')] += n
    assert sum(P.values()) == 110553 and sum(T.values()) == 22461
    assert sum(r*(T[r]-P[r]) for r in T.keys()|P.keys()) == 1424
    return paid, target, P, T, copies


def round_interval(a, b):
    a, b = a*GRID, b*GRID
    return F(a.numerator//a.denominator, GRID), F(-((-b.numerator)//b.denominator), GRID)


@cache
def log_unit(x):
    y = (x-1)/(x+1)
    p = sum((2*y**j/j for j in range(1, 111, 2)), F(0))
    return round_interval(p, p+2*y**111/(111*(1-y*y)))


@cache
def power(rank, k):
    e = rank.bit_length()-1
    lo,hi = [q+e*d for q,d in zip(log_unit(F(rank, 2**e)),log_unit(F(2)),strict=True)]

    def exp_negative(x, n):
        term = total = F(1)
        assert 0 <= x < 1
        for i in range(1,n+1):
            term *= -x/i
            total += term
        return total

    return round_interval(rank*exp_negative(k*hi, 39), rank*exp_negative(k*lo, 40))


def moment(P, T, k):
    lower = upper = F(0)
    for r in P.keys()|T.keys():
        n = T[r]-P[r]
        lo,hi = power(r,k)
        if n < 0:
            lo,hi = hi,lo
        lower += n*lo
        upper += n*hi
    return lower,upper


def slope(rank):
    a,b = power(rank,TARGET)
    c,d = power(rank-1,TARGET)
    return a-d,b-c


def stock(paid, target, copies, baseline, paid_ranks, target_ranks):
    eligible_paid = sorted(((slope(r)[1],r) for r in paid_ranks for _ in range(paid[r])),reverse=True)
    eligible_target = sorted((slope(r)[0],r) for r in target_ranks for _ in range(target[r]))
    price = F(0)
    use_paid, use_target = Counter(), Counter()
    for (upper,p),(lower,t) in zip(eligible_paid,eligible_target):
        if upper <= lower:
            break
        price += upper-lower
        use_paid[p] += 1
        use_target[t] += 1
    saving = copies*price
    return {'eligible_paid':len(eligible_paid), 'eligible_targets':len(eligible_target),
            'selected_paid':dict(use_paid),'selected_targets':dict(use_target),
            'optimistic_pairs':sum(use_paid.values()), 'signed_saving_upper':str(saving),
            'signed_target_net_upper':str(baseline+saving)}


def run(old, peer, seconds):
    deadline = monotonic()+seconds
    before, before_receipt, caller, after, after_receipt = load(old,peer)
    previous, next_ = invoice(before,caller), invoice(after,caller)
    assert next_[4] == previous[4] == 17
    delta = lambda a,b:{r:a[r]-b[r] for r in a.keys()|b.keys() if a[r]!=b[r]}
    assert delta(next_[0],previous[0]) == {4:1,5:-1}
    assert delta(next_[1],previous[1]) == {8:1,9:-1}
    result = {}
    for name, (p,t,P,T,n), receipt, claim in zip(('7244','7274'),(previous,next_),
                                             (before_receipt,after_receipt),CLAIMS,strict=True):
        frozen = receipt['price']['after']
        assert P == {int(r):v for r,v in frozen['P'].items()}
        assert T == {int(r):v for r,v in frozen['T'].items()}
        # Known-good signed prices and a missing-call mutation.
        removed_call = P.copy()
        removed_call[1] -= 1
        assert removed_call != {int(r):v for r,v in frozen['P'].items()}
        a,b = map(F,receipt['price']['price']['independent_raw_bracket'])
        low, high = moment(P,T,a), moment(P,T,b)
        assert low[0]>0 and high[1]<0 and a>claim
        deficit = moment(P,T,TARGET)
        scopes = {label:stock(p,t,n,deficit[1],pr,tr) for label,pr,tr in (
            ('same_delta',{5},{9}),('rank9_target',set(p)-{1},{9}),
            ('any_one_step',set(p)-{1},set(t)-{1}))}
        result[name]={'native_paid':dict(p),'native_target':dict(t),'paid':dict(P),'target':dict(T),
                      'crossing_interval':[str(a),str(b)],'crossing_sign_controls':[str(low[0]),str(high[1])],
                      'claim':str(claim),'target_raw_interval':list(map(str,deficit)),'scopes':scopes}
    assert F(result['7244']['crossing_interval'][1]) < F(result['7274']['crossing_interval'][0])
    assert moment(previous[2],previous[3],CLAIMS[1])[1]<0
    assert monotonic()<deadline, '180-second cap'
    print(json.dumps({'status':'PASS_INDEPENDENT_SIGNED_PRICE_AND_STOCK_CEILINGS',
                      'pins':PINS,'target':str(TARGET),'peer_claim_gain':str(CLAIMS[1]-CLAIMS[0]),
                      'signed_rank_surplus':1424,'proofs':result},indent=2,sort_keys=True))


if __name__ == '__main__':
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('old_root',type=Path)
    cli.add_argument('peer_root',type=Path)
    cli.add_argument('--seconds',type=int,default=180,choices=range(1,181),metavar='1..180')
    a=cli.parse_args()
    run(a.old_root.resolve(),a.peer_root.resolve(),a.seconds)
