#!/usr/bin/env python3
"""Separate set-intersection/Fraction oracle; imports no project code.

Copyright 2026 Ross Richardson. Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse
import random
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def demand(condition, message):
    if not condition:
        raise ValueError(message)


def rational_rank(matrix):
    if not matrix:
        return 0
    rows=[[Fraction(v) for v in row] for row in matrix]
    used=0
    for col in range(len(rows[0])):
        pivot=next((i for i in range(used,len(rows)) if rows[i][col]),None)
        if pivot is None:
            continue
        rows[used],rows[pivot]=rows[pivot],rows[used]
        scalar=rows[used][col]
        rows[used]=[v/scalar for v in rows[used]]
        for i in range(used+1,len(rows)):
            scalar=rows[i][col]
            if scalar:
                rows[i]=[v-scalar*w for v,w in zip(rows[i],rows[used])]
        used+=1
        if used==len(rows):
            break
    return used


def calculate():
    certificate=json.loads((ROOT/'CERTIFICATE.json').read_text())
    points=[frozenset(2*i+((x>>i)&1) for i in range(5)) for x in range(32)]
    even=[x for x,p in enumerate(points) if sum(t%2 for t in p)%2==0]
    odd=[x for x in range(32) if x not in even]
    bitsets=[sum(1<<x for x in side) for side in (even,odd,list(range(32)))]
    e,o,full=bitsets
    matrix=[[2*(len(p&q)-1)*(len(p&q)-3) for q in points] for p in points]
    b=[[len(p&q)%2 for q in points] for p in points]
    demand(all(b[x][y]==int((x in even)==(y in even)) for x in range(32) for y in range(32)),
           'independent decoder geometry')
    for side in (even,odd):
        demand(all(matrix[x][y]==16*int(x==y) for x in side for y in side),'clique identity')
    cross=[[matrix[x][y]//2 for y in odd] for x in even]
    demand(cross==certificate['cross_matrix'],'cross block')
    # Check columns, independently of the primary row-Gram check.
    demand(all(sum(cross[k][i]*cross[k][j] for k in range(16))==64*int(i==j)
               for i in range(16) for j in range(16)),'cross column identity')
    demand(rational_rank(matrix)==16,'rational Gram rank')
    cache={}
    def price(f,g):
        key=(f,g)
        if key not in cache:
            cache[key]=rational_rank([[matrix[x][y] for y in range(32) if g>>y&1]
                                    for x in range(32) if f>>x&1])
        return cache[key]
    def decode(pairs):
        demand(all(f and g for f,g in pairs),'nonzero terms')
        for x in range(32):
            actual=0
            for f,g in pairs:
                if f>>x&1:
                    actual^=g
            demand(actual==(e if x in even else o),'literal full matrix identity')
    # Exhaust every affine factorization after independently justified rank reduction.
    forms=[]
    for constant in (0,1):
        for subset in range(32):
            values=[(constant+sum(((x>>i)&1) for i in range(5) if subset>>i&1))%2
                    for x in range(32)]
            forms.append(sum(v<<x for x,v in enumerate(values)))
    rank_table=[[f,h,price(f,h)] for f in bitsets for h in forms if h]
    rank_digest=sha256(json.dumps(rank_table,sort_keys=True,separators=(',', ':')).encode()).hexdigest()
    demand(rank_digest==certificate['affine_three_term']['rank_table_sha256'],'complete affine rank table')
    hist=Counter(); count=0
    for readers in combinations_with_replacement(bitsets,3):
        if len(set(readers))==1:
            continue
        lastrow=next(x for x in range(32) if readers[2]>>x&1)
        for s0 in forms[1:]:
            for s1 in forms[1:]:
                s2=e if lastrow in even else o
                if readers[0]>>lastrow&1:
                    s2^=s0
                if readers[1]>>lastrow&1:
                    s2^=s1
                if not s2 or s2 not in forms:
                    continue
                sources=[s0,s1,s2]
                # Only the two parity row classes need testing here.
                rows=[]
                for x in (even[0],odd[0]):
                    value=0
                    for f,s in zip(readers,sources):
                        if f>>x&1:
                            value^=s
                    rows.append(value)
                if rows!=[e,o]:
                    continue
                pairs=list(zip(readers,sources)); decode(pairs)
                hist[sum(price(f,g) for f,g in pairs)]+=1; count+=1
    demand(count==433,'complete affine template count')
    demand({str(k):v for k,v in sorted(hist.items())}==certificate['affine_three_term']['cost_histogram'],
           'independent affine cost histogram')
    dense=certificate['dense_rank_checks']
    rng=random.Random(46)
    intended={rng.getrandbits(32) for _ in range(256)}
    intended.update(forms)
    fixed=sum(1<<x for x in even if not (x>>1&1))
    intended.update([fixed,full^fixed])
    intended-={0,e,o}
    demand(set(dense)=={str(h) for h in intended},'complete dense sample domain')
    for h,expected in dense.items():
        mask=int(h); pairs=[(e,e^mask),(o,o^mask),(full,mask)]; decode(pairs)
        got=[price(f,g) for f,g in pairs]
        demand(got==expected,'dense Fraction prices')
    # Every equality mask, with full scalar decoder checks. Cost follows from
    # the checked clique identity; one representative of each size gets dense ranks.
    equality=0; eq_digest=sha256()
    for side in (even,odd):
        for pattern in range(1,(1<<16)-1):
            mask=sum(1<<x for i,x in enumerate(side) if pattern>>i&1)
            pairs=[(e,e^mask),(o,o^mask),(full,mask)]; decode(pairs)
            eq_digest.update(mask.to_bytes(4,'little')); equality+=1
        for size in range(1,16):
            mask=sum(1<<x for x in side[:size])
            got=[price(e,e^mask),price(o,o^mask),price(full,mask)]
            demand(sum(got)==32 and max(got)==16,'equality ranks for every cardinality')
    demand(equality==131068==certificate['distinct_reader_equality_masks'],'equality census')
    witness=certificate['witness']; decode(witness['pairs'])
    demand([price(f,g) for f,g in witness['pairs']]==[8,16,8],'non-affine witness')
    # Independent adversarial examples for coefficient identity and rank failure.
    broken=[list(v) for v in witness['pairs']]; broken[1][1]^=1
    try:
        decode(broken)
    except ValueError:
        pass
    else:
        raise ValueError('coefficient mutation accepted')
    demand(rational_rank([[0,1,2],[0,2,4],[0,0,3]])==2,'skipped-column control')
    demand(rational_rank([[0,2],[3,4]])==2,'row-swap control')
    # A valid Gram with a sparse orthogonal cross block keeps the floor but
    # admits mixed-parity equality: density is needed for our classification.
    sparse=[[16*int((x%16)==(y%16)) for y in range(32)] for x in range(32)]
    sets=[list(range(16)),list(range(16,32)),list(range(32))]
    hh={0,17}
    ss=[set(sets[0])^hh,set(sets[1])^hh,hh]
    sparse_prices=[rational_rank([[sparse[x][y] for y in sorted(s)] for x in r])
                   for r,s in zip(sets,ss)]
    demand(sum(sparse_prices)==32,'sparse scope counterexample')
    return {'affine_templates':count,'dense_masks':len(dense),'dense_price_cache':len(cache),
            'equality_masks':equality,'equality_digest':eq_digest.hexdigest(),
            'sparse_cross_scope_prices':sparse_prices,
            'method':'literal coordinate-set intersections; Fraction elimination; no primary imports'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-certificate',type=Path)
    args=parser.parse_args()
    receipt=calculate()
    if args.write_certificate:
        with args.write_certificate.open('x') as stream:
            json.dump(receipt,stream,sort_keys=True,indent=2); stream.write('\n')
    else:
        expected=json.loads((ROOT/'INDEPENDENT.json').read_text())
        demand(json.dumps(receipt,sort_keys=True)==json.dumps(expected,sort_keys=True),
               'independent receipt mismatch')
    print('PASS_FIVE_CUBE_THREE_TOTALS_INDEPENDENT affine=433 dense=319 equality_masks=131068')
