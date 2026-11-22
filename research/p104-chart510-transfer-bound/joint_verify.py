# SPDX-License-Identifier: Apache-2.0
"""Verify two chart-510 residual readouts and an ordered abstract support transport.

Usage: python3 -IB joint_verify.py
The authenticated graph, caller, and witness are adjacent by default.
An intersection is an abstract sufficient witness for BOTH support-nonempty
conditions; it is not a test that an actual whole field is zero.
"""
from argparse import ArgumentParser
from array import array
from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import chain
from pathlib import Path
import gzip
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from zero_support import packed_counts

TRIAL=Fraction('0.003890115286594461129996943')
SCALE=10**30
EXPECTED_SHA='1286d70972e70431abfc4433858429a58c6602ff834bf8cad64e3c94ef1476c2'
GRAPH_SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
CALLER_SHA='757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'
# A reads 2335 (clock 10039); B reads 2337 (clock 10036).
READOUTS={
 '90':{'a':[2330,2336,2344,2367,2416,2482,2542],
       'b':[2327,2330,2336,2339,2354,2370,2372,2375,2382,2385,2387,2404,2506,2510,2513,2518,2629]},
 '46':{'a':[2336,2344,2416,2439,2448,2451,2482,2655,2698],
       'b':[2359,2362,2372,2394,2397,2408,2416,2419,2425,2431,2434,2465,2484,2518,2530,2571,2576,2584,2600,2617,2623,2626,2778]},
}
RESIDUALS={
 '90':{'a':[266,268,274,279,291,293,316,322,400,401,407,409,410,413,414,417,421,422,425,428,434,437,445,449,452,500,501,512,513,534,569,570,578,579],
       'b':[225,226,227,233,234,237,240,242,243,245,246,248,249,251,253,254,334,341,342,346,357,360,365,366,367,371,372,374,375,377,381,386,387,388,390,458,461,467,468,469,472,477,484,489,490,509,522,538,539,553,554,556,571,573,589,610]},
 '46':{'a':[266,268,274,279,291,293,316,400,401,407,413,414,421,422,425,428,434,437,445,449,452,500,501,512,513,569,570,578,579],
       'b':[254,255,258,259,276,361,365,367,393,431,442,458,459,465,472,482,497,512]},
}


# Outward log/exp arithmetic from the #8030 independent binary price checker.
GRID = 1 << 112


def grid_bounds(lower, upper):
    lo = lower * GRID
    hi = upper * GRID
    return Fraction(lo.__floor__(), GRID), Fraction(hi.__ceil__(), GRID)


@cache
def log_ratio(z):
    """Enclose 2 atanh(z) by its positive series and a geometric tail."""
    assert 0 <= z <= Fraction(1, 3)
    z2 = z * z
    term = z
    total = Fraction(0)
    for j in range(45):
        total += term / (2 * j + 1)
        term *= z2
    return grid_bounds(2 * total, 2 * (total + term / (91 * (1 - z2))))


@cache
def log_rank(rank):
    """Reduce the argument to [1,2] before evaluation."""
    k = rank.bit_length() - 1
    radix = 1 << k
    low, high = log_ratio(Fraction(rank - radix, rank + radix))
    log2low, log2high = log_ratio(Fraction(1, 3))
    return low + k * log2low, high + k * log2high


def small_exp(x):
    """Use the first 32 terms and bound all later term ratios by x/33."""
    assert 0 <= x <= 1
    term = total = Fraction(1)
    for j in range(1, 32):
        term *= x / j
        total += term
    next_term = term * x / 32
    return grid_bounds(total, total + next_term / (1 - x / 33))


@cache
def rank_price(rank, exponent):
    low, high = log_rank(rank)
    assert exponent >= 0
    a, _ = small_exp(low * exponent / 16)
    _, b = small_exp(high * exponent / 16)
    return grid_bounds(a**16, b**16)



def bits(mask):
    out=[]
    while mask:
        bit=mask&-mask; out.append(bit.bit_length()-1); mask^=bit
    return out


def run(g,program):
    """Replay all independent formal fields and the exact chart/owner lifetime."""
    n=g['public']; frame=dict(enumerate(g['start'])); val={i:1<<i for i in range(n)}
    cleared=[]; scratch={}
    needed={2335,2337}|{i for variants in READOUTS.values() for path in variants.values() for i in path}
    for clock,(op,d,*args) in enumerate(program):
        if program is g['program'] and clock==10034:
            scratch={i:val[i] for i in needed}
        if op=='INIT':
            assert d>=n and d not in frame
            frame[d]=args[0]; val[d]=0
        elif op=='ADD':
            s,c=args; assert frame[d]==frame[s]==c
            val[d]^=val[s]
        elif op=='MOVE':
            before,after=args; assert frame[d]==before; frame[d]=after
        elif op=='SWAP':
            s,=args;frame[d],frame[s]=frame[s],frame[d];val[d],val[s]=val[s],val[d]
        elif op=='CLEAR':
            assert d>=n and frame.pop(d)==args[0]
            cleared.append((args[0],val.pop(d)))
        else: raise AssertionError(op)
    assert frame==dict(enumerate(g['final'])) and set(val)==set(range(n))
    return val,cleared,scratch


def readout(g,words,which):
    p=g['program']
    if which=='b':
        return p[:10034]+[['INIT',2828,1]]+[['ADD',2828,s,1] for s in words]+p[10037:]
    return p[:10037]+[['INIT',2829,1]]+[['ADD',2829,s,1] for s in words]+p[10040:]


def inspect_readouts(g):
    p=g['program']; n=g['public']
    assert n==630
    assert p[10034:10040]==[['INIT',2828,510],['ADD',2828,2337,510],['MOVE',2828,510,1],['INIT',2829,510],['ADD',2829,2335,510],['MOVE',2829,510,1]]
    assert p[11014:11018]==[['INIT',3151,510],['ADD',3151,2335,510],['ADD',3151,2337,510],['MOVE',3151,510,328]]
    original,old_clear,scratch=run(g,p)
    for i in range(n):
        expected=1<<i
        if 111<=i<222: expected^=1<<(i-111)
        assert original[i]==expected
    dims={int(i):e['dim'] for i,e in g['frames'].items()}
    def paid_hist(program):
        return Counter(abs(dims[row[2]]-dims[row[3]]) for row in program if row[0]=='MOVE')
    before=paid_hist(p)
    for alt in READOUTS:
        for which in ('a','b'):
            old=scratch[2335 if which=='a' else 2337]
            for i in READOUTS[alt][which]: old^=scratch[i]
            residual=old
            assert bits(residual)==RESIDUALS[alt][which]
            assert residual&((1<<222)-1)==0
            candidate=readout(g,READOUTS[alt][which],which)
            after=paid_hist(candidate)
            assert before-after==Counter({1:1}) and not after-before
            new,new_clear,_=run(g,candidate)
            assert [chart for chart,_ in new_clear]==[chart for chart,_ in old_clear]
            assert len(new_clear)==3433
            # Under the independent helper-zero premise, every output is the same;
            # all other 630 - |residual| input fields stay arbitrary.
            assert all((original[i]^new[i])&~residual==0 for i in range(n))
            # Erasure owners and charts are retained. Their actual dirty payloads
            # need not match, and still receive their ordinary paid scrub.
    return RESIDUALS


def inputs(g,c,rank_price):
    targets,paid,labels=packed_counts(g,c)
    lookup={v:i for i,(_,v) in enumerate(targets)}
    intersections=[];changed=0;refined=[]
    for (r,support),label in zip(paid,labels,strict=True):
        if label[0]=='move' and label[2] in (10036,10039):
            _,when,clock=label;which='b' if clock==10036 else 'a'
            old=set(support)
            z46={lookup['helper',when,h] for h in RESIDUALS['46'][which]}
            z90={lookup['helper',when,h] for h in RESIDUALS['90'][which]}
            support=tuple(sorted(old&z46&z90))
            helper=[targets[i][1][2] for i in support]
            assert helper==([365,367] if clock==10036 else [428,437,445,452])
            assert r==1 and all(targets[i][0]==8 for i in z46|z90)
            intersections.append((when,clock,helper));changed+=1
        refined.append((r,support))
    assert changed==72 and len(intersections)==72
    prices={r:rank_price(r,1-TRIAL) for r in {r for r,_ in targets+refined}}
    demand=[(prices[r][1]*SCALE).__ceil__() for r,_ in targets]
    grouped=Counter()
    for r,support in refined:
        ordered=tuple(i for i in support if targets[i][0]>=r)
        assert ordered
        grouped[r,ordered]+=1
    supply=[((prices[r][0]*SCALE).__floor__()*count,r,array('I',support)) for (r,support),count in grouped.items()]
    return demand,supply


def check(demand,supply,stream):
    assert int(next(stream))==0
    left=demand.copy();spent=[0]*len(supply);count=0
    for line in stream:
        i,j,x=map(int,line.split())
        if not (0<=i<len(demand) and 0<=j<len(supply) and x>0 and i in supply[j][2]):
            raise ValueError('Invalid or unordered transport edge')
        left[i]-=x;spent[j]+=x;count+=1
    if any(left) or any(x>m for x,(m,_,_) in zip(spent,supply,strict=True)):
        raise ValueError('Unpaid target or overspent paid slot')
    return count


def pinned_json(path,digest):
    data=path.read_bytes()
    if sha256(data).hexdigest()!=digest:
        raise ValueError(f'Wrong source bytes: {path.name}')
    return json.loads(gzip.decompress(data))


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--graph',type=Path,default=HERE/'strong-bit.json.gz')
    parser.add_argument('--caller',type=Path,default=HERE/'EFREE-CALLER.json.gz')
    parser.add_argument('--certificate',type=Path,default=HERE/'TRANSPORT.txt.gz')
    args=parser.parse_args()
    certificate=args.certificate
    if sha256(certificate.read_bytes()).hexdigest()!=EXPECTED_SHA:
        raise ValueError('Transport witness does not match its authenticated digest')
    g=pinned_json(args.graph,GRAPH_SHA)
    c=pinned_json(args.caller,CALLER_SHA)
    inspect_readouts(g)
    demand,supply=inputs(g,c,rank_price)
    assert (len(demand),len(supply),sum(len(s) for _,_,s in supply))==(18906,86802,6729066)
    with gzip.open(certificate,'rt') as f: count=check(demand,supply,f)
    assert count==114405
    with gzip.open(certificate,'rt') as f:
        header=next(f);i,j,x=map(int,next(f).split())
        try:check(demand,supply,chain((header,f'{i} {j} {x-1}\n'),f))
        except ValueError as error:
            assert 'Unpaid target' in str(error)
        else: raise AssertionError('One-tick corruption was accepted')
    print(json.dumps({'trial':str(TRIAL),'scale':SCALE,'targets':len(demand),'paid_groups':len(supply),'ordered_arcs':sum(len(s) for _,_,s in supply),'certificate_arcs':count,'certificate_sha256':EXPECTED_SHA,'readouts_checked':4,'joint_intersections_per_call':[[365,367],[428,437,445,452]],'one_tick_corruption_rejected':True}))
    print('PASS_JOINT_SUPPORT_TRANSPORT')


if __name__=='__main__':main()
