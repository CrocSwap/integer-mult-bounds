#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exhaust every labeled triple rectangle at h=5..10 with set arithmetic."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from math import comb
from pathlib import Path

HERE=Path(__file__).resolve().parent


def check(ok,why):
    if not ok:
        raise ValueError(why)


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)


def census(h):
    triples=list(map(frozenset,combinations(range(h),3)))
    total=Counter();patterns=Counter()
    for a,b in combinations(triples,2):
        if len(a&b)!=1:
            continue
        total['source_pairs']+=1
        counts=Counter()
        possible=[t for t in triples if len(t&a)%2==len(t&b)%2==0]
        source_space={frozenset(),a,b,a^b}
        for c,d in combinations(possible,2):
            if len(c&d)!=1:
                continue
            total['eligible_rectangles']+=1
            counts['cross_orthogonal_degenerate']+=1
            # Exact rational 2x2 determinant, separate from the bit-mask engine.
            x,y,z,w=[Fraction(1 if len(s&t)==0 else -1) for s,t in [(a,c),(a,d),(b,c),(b,d)]]
            if x*w-y*z:
                counts['scalar_rank_two']+=1
                continue
            counts['scalar_rank_one']+=1
            target_space={frozenset(),c,d,c^d}
            if source_space&target_space!={frozenset()}:
                counts['common_radical']+=1
                continue
            counts['admissible_algebraic_rectangles']+=1
            total['accepted']+=1
            check(not (a|b)&(c|d),'unexpected intersecting supports')
        counts['admissible_algebraic_rectangles']+=0
        patterns[tuple(sorted(counts.items()))]+=1
    check(len(patterns)==1,'coordinate-permutation count invariance')
    fixed=15*comb(h-5,5) if h>=10 else 0
    check(total['source_pairs']==15*comb(h,5) and total['accepted']==15*comb(h,5)*fixed,'closed count formula')
    return dict(ambient=h,source_pairs=total['source_pairs'],eligible_rectangles=total['eligible_rectangles'],
                accepted=total['accepted'],per_source_counts=dict(next(iter(patterns))))


def run():
    source=json.loads((HERE/'CERTIFICATE.json').read_text(encoding='utf8'))
    rows=[census(h) for h in range(5,11)]
    for row,expected in zip(rows,source['census']):
        check(row['ambient']==expected['ambient'] and row['per_source_counts']==expected['counts'],'canonical/labeled census agreement')
        check(row['accepted']==expected['all_labeled_rectangles'],'labeled count binding')
    return dict(schema='independent-triple-rectangles/1',method='all labeled sets and exact Fraction determinants; no imported checker',
                rows=rows,source_pairs=sum(r['source_pairs'] for r in rows),eligible_rectangles=sum(r['eligible_rectangles'] for r in rows),
                accepted=sum(r['accepted'] for r in rows))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-certificate',action='store_true');args=parser.parse_args()
    result=run();path=HERE/'INDEPENDENT.json'
    if args.write_certificate:
        check(not path.exists(),'refusing independent certificate overwrite')
        path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    check(canonical(result)==canonical(json.loads(path.read_text(encoding='utf8'))),'independent certificate mismatch')
    print('PASS_INDEPENDENT_TRIPLE_THRESHOLD: source_pairs=%d eligible_rectangles=%d accepted=%d' % (result['source_pairs'],result['eligible_rectangles'],result['accepted']))


if __name__=='__main__':
    main()
