#!/usr/bin/env python3
"""Integer-only packed-cost crosscheck; imports no primary checker. Apache-2.0."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 20
MASK = (1 << WIDTH)-1
NS = tuple(range(-543,0)) + tuple(range(1,544))


def demand(value, reason):
    if not value:
        raise ValueError(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def cost(n, denominator_power):
    if not n:
        return 0
    n = abs(n)
    while denominator_power and n % 2 == 0:
        n //= 2
        denominator_power -= 1
    count = 3 + denominator_power
    while n:
        count += n % 2
        n //= 2
        if n:
            count += 1
    return count


def check():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    path=next(p for p in pins['files'] if p.endswith('CANONICAL-WORD.json.gz'))
    payload=gzip.decompress((ROOT/path).read_bytes())
    demand(hashlib.sha256(payload).hexdigest()==pins['files'][path]['sha256'],'word pin')
    word=json.loads(payload)
    rows=[[0]*492 for _ in range(112)]
    for op,t,s,a,b,f in word['compensation']:
        demand(op=='add' and f==0 and (4*a)%b==0,'panel')
        rows[t-112][s-224]=(4*a)//b
    grouped={}
    for t,left in enumerate(rows):
        for p,right in enumerate(rows):
            if t==p:
                continue
            hist=tuple(sorted(Counter((a,b) for a,b in zip(left,right) if a or b).items()))
            grouped.setdefault(hist,[]).append((t+112,p+112))
    # Each lane is a complete coefficient price; explicit bound prevents carries.
    # At most 492 residual cells and two boundary shears; all terms <= 32.
    demand((492+2)*32 < (1<<WIDTH),'packed carry bound')
    scalar={}
    for a in range(-4,5):
        for b in range(-4,5):
            if a or b:
                terms=[cost(8*a-n*b,5) for n in NS]
                demand(max(terms)<=32,'scalar lane bound')
                scalar[a,b]=sum(term<<(WIDTH*i) for i,term in enumerate(terms))
    boundary_terms=[2*cost(n,3) for n in NS]
    demand(max(boundary_terms)<=64,'boundary lane bound')
    boundary=sum(term<<(WIDTH*i) for i,term in enumerate(boundary_terms))
    margins=Counter()
    best=best_root=None
    root_winners=0
    summaries=[]
    for hist,pairs in sorted(grouped.items()):
        encoded=boundary+sum(count*scalar[pair] for pair,count in hist)
        costs=[]
        for n in NS:
            costs.append(encoded&MASK)
            encoded >>= WIDTH
        demand(encoded==0,'packed overflow')
        root=sum(count*cost(a,2) for (a,b),count in hist)
        baseline=min(root,costs[535],costs[550]) # n=-8 and n=+8
        demand(NS[535]==-8 and NS[550]==8,'unit indices')
        least=None
        for n,value in zip(NS,costs):
            if abs(n)==8:
                continue
            gap=value-baseline
            demand(gap>0,'nonunit improvement')
            margins[gap]+=len(pairs)
            root_winners+=len(pairs)*(value<root)
            candidate=(gap,*min(pairs),n)
            root_candidate=(value-root,*min(pairs),n)
            best=candidate if best is None else min(best,candidate)
            best_root=root_candidate if best_root is None else min(best_root,root_candidate)
            least=gap if least is None else min(least,gap)
        summaries.append([list(map(list,hist)),len(pairs),digest(costs),least])
    result={'ordered_pairs':12432,'coefficient_count':len(NS),'finite_cases':12432*len(NS),
            'nonunit_cases':sum(margins.values()),'histogram_groups':len(grouped),
            'minimum_domination':list(best),'minimum_root_margin':list(best_root),
            'nonunit_edges_beating_root':root_winners,
            'margin_histogram':{str(k):v for k,v in sorted(margins.items())},
            'group_costs_sha256':digest(summaries)}
    expected=json.loads((HERE/'EXPECTED.json').read_text())['finite']
    demand(result==expected,'independent full census mismatch')
    print('PASS_CK_PACKED_ORACLE cases=13501152 exact_lane_bits=20 full_receipt_match')


if __name__=='__main__':
    check()
