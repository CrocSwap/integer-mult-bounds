#!/usr/bin/env python3
"""Check the changed native map and its composition in the literal 36-call caller.

Run: python3 -IB review.py strong-bit.json.gz EFREE-CALLER.json.gz

Standard library only, with two byte-pinned inputs supplied on the command
line. Outer-call checks restrict physical fields to constant binary fields,
on which every address permutation/route is the identity. All root and helper
inputs are separate formal bits. This subset witnesses loss of information.
The separately reviewed #8035 adapter binds each LOCAL helper to the distinct
owner tag ("helper", clock, i); the two supplied tapes do not encode that
adapter or prove this ownership premise by themselves.
"""
import argparse
from collections import Counter
from functools import reduce
from hashlib import sha256
from itertools import chain
import gzip
import json
from operator import xor
from pathlib import Path

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('graph',type=Path)
ap.add_argument('caller',type=Path)
args = ap.parse_args()
graph_bytes,caller_bytes = args.graph.read_bytes(),args.caller.read_bytes()
assert sha256(graph_bytes).hexdigest() == '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
assert sha256(caller_bytes).hexdigest() == '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'
G = json.loads(gzip.decompress(graph_bytes))
C = json.loads(gzip.decompress(caller_bytes))
P = G['program']
N = G['public']
assert N == 630

# Independently construct the literal changed program.
A = [2336,2344,2416,2439,2448,2451,2482,2655,2698]
B = [2359,2362,2372,2394,2397,2408,2416,2419,2425,2431,2434,2465,2484,2518,2530,2571,2576,2584,2600,2617,2623,2626,2778]
assert P[10034:10040] == [['INIT',2828,510],['ADD',2828,2337,510],['MOVE',2828,510,1],['INIT',2829,510],['ADD',2829,2335,510],['MOVE',2829,510,1]]
Q = P[:10034] + [['INIT',2828,1]] + [['ADD',2828,i,1] for i in B] + [['INIT',2829,1]] + [['ADD',2829,i,1] for i in A] + P[10040:]

def run(program):
    chart = dict(enumerate(G['start']))
    val = {i:1 << i for i in range(N)}
    for op,d,*args in program:
        if op == 'INIT':
            assert d not in chart
            chart[d], val[d] = args[0], 0
        elif op == 'ADD':
            s,c = args
            assert chart[d] == chart[s] == c
            val[d] ^= val[s]
        elif op == 'SWAP':
            s, = args
            chart[d],chart[s] = chart[s],chart[d]
            val[d],val[s] = val[s],val[d]
        elif op == 'MOVE':
            u,v = args
            assert chart[d] == u
            chart[d] = v
        elif op == 'CLEAR':
            assert chart.pop(d) == args[0]
            del val[d]
        else:
            raise AssertionError(op)
    assert chart == dict(enumerate(G['final'])) and set(val) == set(range(N))
    return [val[i] for i in range(N)]

def bits(x):
    return [i for i in range(x.bit_length()) if x >> i & 1]

def parity(x):
    return x.bit_count() % 2

def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            k = row.bit_length()
            if k not in pivots:
                pivots[k] = row
                break
            row ^= pivots[k]
    return len(pivots)

def apply(rows, x):
    return sum(parity(row & x) << i for i,row in enumerate(rows))

orig, changed = run(P),run(Q)
assert all(orig[i] == ((1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0)) for i in range(N))
ra = sum(1 << i for i in [266,268,274,279,291,293,316,400,401,407,413,414,421,422,425,428,434,437,445,449,452,500,501,512,513,569,570,578,579])
rb = sum(1 << i for i in [254,255,258,259,276,361,365,367,393,431,442,458,459,465,472,482,497,512])
sa = sum(1 << i for i in [92,99,231,428,433,434,435,448,449,473,516,582])
sb = sum(1 << i for i in [63,222,230,362,367,368,369])
assert all((orig[i]^changed[i]) == ((ra if sa>>i&1 else 0)^(rb if sb>>i&1 else 0)) for i in range(N))
assert rank([ra,rb]) == rank([sa,sb]) == 2
assert rank(orig) == 630 and rank(changed) == 628

# Local helper output block: H'=(I+U^h R)H.  No main input enters H'.
assert all(not (changed[i] & ((1 << 222)-1)) for i in range(222,630))
assert all((changed[i] & ((1 << 222)-1)) == orig[i] & ((1 << 222)-1) for i in range(222))
helper_coupling = [[parity(r & s) for s in (sa,sb)] for r in (ra,rb)]
assert helper_coupling == [[1,0],[0,1]]
assert rank(changed[222:]) == 406
assert reduce(xor,(changed[i] for i in bits(ra)),0) == 0
assert reduce(xor,(changed[i] for i in bits(rb)),0) == 0

# M is the main-pair CNOT and is its own inverse. Read its inverse on S.
ka,kb = apply(orig,sa),apply(orig,sb)
coupling = [[parity(r & k) for k in (ka,kb)] for r in (ra,rb)]
assert coupling == [[1,0],[0,1]]
assert apply(changed,ka) == apply(changed,kb) == 0
assert apply(orig,ka) == sa and apply(orig,kb) == sb

assert C['ports']==111 and C['roles']==38
assert Counter(row[0] for row in C['events']) == {'ADD':362,'SWAP':364,'LOCAL':36,'IDLE_ONE':32,'QUERY':4}
total = 38*111+36*408
assert total == 18906
asig,bsig = bits(sa),bits(sb)
ares,bres = bits(ra),bits(rb)

def outer(changed_calls):
    roots = [[1 << (r*111+p) for p in range(111)] for r in range(38)]
    helper_outputs = []
    local_number = 0
    for row in C['events']:
        op,*args = row
        if op == 'LOCAL':
            stage,x,y = args
            helpers = [1 << (38*111+local_number*408+i) for i in range(408)]
            # Original normalized native transform, valid at all constant fields.
            for p in range(111):
                roots[y][p] ^= roots[x][p]
            if local_number in changed_calls:
                aval = reduce(xor,(helpers[i-222] for i in ares),0)
                bval = reduce(xor,(helpers[i-222] for i in bres),0)
                for signature,value in ((asig,aval),(bsig,bval)):
                    for i in signature:
                        if i < 111:
                            roots[x][i] ^= value
                        elif i < 222:
                            roots[y][i-111] ^= value
                        else:
                            helpers[i-222] ^= value
            helper_outputs.extend(helpers)
            local_number += 1
        elif op in ('ADD','QUERY'):
            x,y = args
            for p in range(111):
                roots[x][p] ^= roots[y][p]
        elif op == 'SWAP':
            x,y = args
            roots[x],roots[y] = roots[y],roots[x]
        elif op == 'IDLE_ONE':
            pass
        else:
            raise AssertionError(row)
    assert local_number == 36
    return list(chain.from_iterable(roots)),helper_outputs

outer_results = {}
cases = {f'first_{m}':set(range(m)) for m in (0,1,2,18,25,36)}
cases.update({'last_1':{35},'even_18':set(range(0,36,2)),
              'last_25':set(range(11,36))})
for label, selected in cases.items():
    m = len(selected)
    rootrows,helpers = outer(selected)
    total_rank = rank(chain(rootrows,helpers))
    helper_rank = rank(helpers)
    # This establishes independent full-rank root input freedom, despite all
    # local-pair roots being shared and correlated across the 36 invocations.
    root_restriction = rank(r & ((1 << (38*111))-1) for r in rootrows)
    assert total_rank == total-2*m
    assert helper_rank == 36*408-2*m
    assert root_restriction == 38*111
    if m == 0:
        assert rootrows == [1 << i for i in range(38*111)]
        assert helpers == [1 << i for i in range(38*111,total)]
    outer_results[label] = {'m':m,'rank':total_rank,'nullity':total-total_rank,'helper_output_rank':helper_rank,'root_input_restriction_rank':root_restriction}

print(json.dumps({'original_rank':rank(orig),'changed_rank':rank(changed),'residual_signature_coupling':coupling,'helper_residual_signature_coupling':helper_coupling,'changed_helper_rank':rank(changed[222:]),'collision_a_nonzero_input':bits(ka),'collision_b_nonzero_input':bits(kb),'collision_a_original_output':bits(sa),'collision_b_original_output':bits(sb),'caller_model':'constant binary fields; independent 38*111 root and 36*408 per-call helper fields; unique helper owners at each LOCAL','caller_rows':total,'caller_cases':outer_results,'all_subset_rank':'18906-2m, by block triangularity and distinct helper owners'},indent=2,sort_keys=True))
