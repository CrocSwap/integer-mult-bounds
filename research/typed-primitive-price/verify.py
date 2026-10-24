#!/usr/bin/env python3
"""Source-bound primitive-price comparison. Apache-2.0; Codex assistance."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(*values):
    return tuple(sum(v[i] for v in values) for i in (0, 1))


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'Live interval engine pin')
    for row in json.loads((HERE/'FROZEN-INPUTS.json').read_text()):
        raw = (HERE/row['snapshot']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'Frozen source bytes')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'Frozen Git blob')


def engine():
    path = ROOT/'research/higher-moment-strictification/verify.py'
    spec = importlib.util.spec_from_file_location('primitive_price_intervals', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def typed_profiles():
    word = json.loads(gzip.decompress((HERE/'inputs/typed-word.json.gz').read_bytes()))
    c = word['canonical']
    H = Counter()
    for role in range(224, 632):
        a, b = (c['frames'][c[key][role]] for key in ('start','final'))
        def span(basis):
            s = {0}
            for x in basis:
                s |= {v^x for v in tuple(s)}
            return s
        need(span(a) <= span(b), 'Nested arbitrary helper interface')
        H[len(b)-len(a)] += 1
    profiles = []
    for direction in ('forward','backward'):
        P = Counter()
        for event in word['programs'][direction]:
            if event[0] in ('climb','center','cache_child'):
                rank = event[-1]
                old, new = event[-3:-1]
                need(rank == abs(len(c['frames'][new])-len(c['frames'][old])), 'Emitted paid rank')
                P[rank] += 1
        profiles.append(P)
    need(profiles[0] == profiles[1], 'Both emitted paid censuses')
    need(H == {3:2,6:7,7:47,8:139,9:213}, 'Typed helper census')
    need(profiles[0] == {1:2177,2:424,3:389,4:147,5:50,8:8}, 'Typed paid census')
    return H, profiles[0]


# Exact Laurent polynomials, with commuting symbols D and Q. No finite order.
def plus(a, b):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0)+value
    return {k:v for k,v in out.items() if v}


def times(a, b):
    out = {}
    for (d,q), x in a.items():
        for (e,r), y in b.items():
            k = (d+e,q+r)
            out[k] = out.get(k, 0)+x*y
    return {k:v for k,v in out.items() if v}


def mm(a, b):
    return [[plus(times(a[i][0],b[0][j]),times(a[i][1],b[1][j])) for j in range(2)] for i in range(2)]


def mono(d=0,q=0,c=1):
    return {(d,q):c}


def operator_identities():
    one, zero, d, dq = mono(), {}, mono(1), mono(1,1)
    Sy = [[one,zero],[mono(q=-1),one]]
    A = [[d,zero],[mono(1,-1),d]]
    B = [[d,zero],[d,dq]]
    need(mm([[d,zero],[zero,d]], Sy) == A, 'Direct forward type A')
    need(mm([[one,zero],[one,one]], [[d,zero],[zero,dq]]) == B, 'Direct forward type B')
    # The direct inverse transposes are literal transposes of inverses.
    Adual = [[mono(-1),mono(-1,-1,-1)],[zero,mono(-1)]]
    Bdual = [[mono(-1),mono(-1,-1,-1)],[zero,mono(-1,-1)]]
    Ax = [[one,mono(q=-1,c=-1)],[zero,one]]
    Bx = [[one,mono(c=-1)],[zero,one]]
    need(mm([[mono(-1),zero],[zero,mono(-1)]], Ax) == Adual, 'Direct raw backward type A')
    need(mm(Bx, [[mono(-1),zero],[zero,mono(-1,-1)]]) == Bdual, 'Direct raw backward type B')
    # Omitting Q from the B diagonal, or replacing Q^-1 by Q, is false.
    need(mm([[one,zero],[one,one]], [[d,zero],[zero,d]]) != B, 'B query is actually paid')
    need(mm([[d,zero],[zero,d]], [[one,zero],[mono(q=1),one]]) != A, 'Q inverse control')


def gap(E, H, P, block, saving):
    t = 1-saving
    return add(E.moment(P,t), E.scale(E.moment(H,t),-1),
               E.scale(E.power(block,t),-224), (Q(-112),)*2)


def certify():
    authenticate()
    E = engine()
    H, P = typed_profiles()
    operator_identities()
    # Normalized derivative lower bounds in PROOF.md retain just rank one.
    log7, log8 = E.log_bounds(7), E.log_bounds(8)
    log76 = add(log7,E.scale(E.log_bounds(6),-1))
    log87 = add(log8,E.scale(log7,-1))
    need(log7[0]>1 and log8[0]>1 and log76[1]<1 and log87[1]<1, 'Elementary log bounds')
    need(Q(2065,7)-7 == 288 > 0, 'Typed normalized gap increases for all C')
    mass = lambda p:sum(r*n for r,n in p.items())
    need(mass(P)-mass(H)-224*7-112 == 8, 'Every direct helper and central job charged')
    source = json.loads((HERE/'inputs/round3-arithmetic.json').read_bytes())
    Ho = {int(k):n for k,n in source['local_helpers'].items()}
    Po = {int(k):n for k,n in source['local_paid'].items()}
    need(Ho == {4:28,7:7,8:47,9:326}, 'Round-three helper input')
    need(Po == {1:2201,2:412,3:510,4:127,5:40,8:8}, 'Round-three paid input')
    need(Q(2089,8)-7 == Q(2033,8)>0, 'Original normalized gap strictly increases for all C')
    lo, hi = Q('0.0062073960'), Q('0.0062073961')
    below, above = gap(E,Ho,Po,8,lo),gap(E,Ho,Po,8,hi)
    need(below[1]<0 and above[0]>0, 'Unique original discount endpoint')
    samples = {}
    for C in (Q(0),Q('0.003'),Q('0.004'),Q('0.006'),Q('0.01')):
        G = gap(E,H,P,7,C)
        lower = E.scale(E.power(7,-C),8)
        need(G[0]>=lower[1] if C else G[0]<=8<=G[1], 'Uniform typed dominance lower bound')
        samples[str(C)] = {'typed_native_minus_direct':E.display(G),
                          'original_direct_minus_native':E.display(E.scale(gap(E,Ho,Po,8,C),-1))}
    # An actually removed centre reverses the integer boundary; this is a false invoice.
    unpaid = dict(P)
    unpaid[8] -= 2
    need(mass(unpaid)-mass(H)-224*7-112 < 0, 'Unpaid owned jobs control')
    return {'status':'PASS_TYPED_DIRECT_PRIMITIVE_DOMINANCE',
            'scope':'Exact typed ABI and direct helper normalization; local moment comparison only',
            'typed_H':H,'typed_P':P,'direct_main_paid':{'1':112,'7':224},
            'uniform_gap_lower_bound':'8 * 7^(-C), 0<=C<1',
            'normalized_derivative_lower_bound':'288',
            'original_discount_endpoint':[str(lo),str(hi)],
            'original_gap_below':E.display(below),'original_gap_above':E.display(above),
            'samples':samples,'new_kappa':False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--write',action='store_true')
    args = p.parse_args()
    result = json.loads(json.dumps(certify()))
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == result, 'Committed exact receipt')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
