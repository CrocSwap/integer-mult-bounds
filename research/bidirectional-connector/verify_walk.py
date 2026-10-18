#!/usr/bin/env python3
"""Replay charged walk fixtures and their standalone exact/dense failure checks."""
from hashlib import sha256
import json
from pathlib import Path
import random
from fractions import Fraction
import certify_cost
import subprocess
import sys

import independent_check as dense
import verify as primary
import walk

HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--write-receipt',action='store_true')
    args=parser.parse_args()
    fixtures=json.loads((HERE/'WALKS.json').read_text())
    cases=0;omissions=0
    discovery_digest=sha256((HERE/'search_walk.cpp').read_bytes()).hexdigest()
    differences=[]
    for n in (5,6):
        primary_sets={w:certify_cost.difference_set(w) for w in certify_cost.pair_words(n)}
        independent_sets={w:certify_cost.walsh_cover(w,n) for w in certify_cost.matching_words(n)}
        need(primary_sets==independent_sets,'minimum-source dependency engines disagree')
        need(len(primary_sets)==(945 if n==5 else 10395),'incomplete difference census')
        maximum=max(map(len,primary_sets.values()))-1
        need(maximum==walk.source_difference_bound(n),'incorrect minimum-source difference ceiling')
        differences.append({'sources':n,'complete_words':len(primary_sets),'max_nonzero_differences':maximum})
    bound_records=[]
    for record in fixtures['records']:
        need(record['discovery']['source_sha256']==discovery_digest,'proposal source pin drift')
        n=record['sources'];word,counts=walk.construct(record['source_word'],record['colors'])
        need(counts==record['counts'],'walk invoice changed')
        need(sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest()==record['word_sha256'],
             'literal walk changed')
        primary.check_endpoint(word,n,2)
        bound=walk.minimum_source_invoice(n,record['source_price'],1)
        need(int(bound['query_lower_bound'])==record['minimum_source_query_lower_bound'],'minimum-source bound drift')
        if n==9:need(Fraction(record['query_cost'],bound['query_lower_bound'])<=Fraction(103,100),
                     'three-percent restricted gap failed')
        bound_records.append({'sources':n,'readout_lower':bound['readout_lower'],
                              'query_lower_bound':int(bound['query_lower_bound']),
                              'cases':bound['cases'],'scope':bound['scope']})
        names=[f'x{j}' for j in range(n)]+[f'y{m}' for m in range(1,1<<n)]+['z0','z1']
        states=[]
        # Full incoming basis for n9; dirty roots plus mixed states for the
        # n12 fixture with five-read targets. Generic polynomial replay covers all.
        selected=names if n==9 else ['z0','z1','x0','x11','y1','y4095']
        for name in selected:
            for bit in (1,2):
                incoming=dict.fromkeys(names,0);incoming[name]=bit;states.append(incoming)
        rng=random.Random(4097+n)
        states.extend({name:rng.randrange(4) for name in names} for _ in range(8))
        for bank in dense.banks(2,n):
            for incoming in states:
                actual=dense.replay(word,incoming,bank)
                need(actual==dense.direct(incoming,bank,n),'independent walk matrix endpoint')
                need(dense.replay(list(reversed(word)),actual,bank)==incoming,'independent walk inverse')
                cases+=1
        if n==9:
            for index in range(len(word)):
                try:primary.check_endpoint(word[:index]+word[index+1:],n,2)
                except ValueError:omissions+=1
                else:raise ValueError('walk omission accepted')
    receipt={'schema':'minimum-source-bound-v1','difference_censuses':differences,'records':bound_records}
    sweep=json.loads((HERE/'WALK-SWEEP.json').read_text())
    count=0
    for candidate in sweep['records']:
        for choice in candidate['orientations']:
            word,counts=walk.construct(candidate['source_word'],choice['colors'])
            need(counts==choice['counts'],'sweep invoice drift')
            need(sha256(json.dumps(word,separators=(',',':')).encode()).hexdigest()==choice['word_sha256'],'sweep word drift')
            primary.check_endpoint(word,candidate['sources'],2);count+=1
    need(count==114,'incomplete retained 19-partition/six-orientation sweep')
    subprocess.run([sys.executable,'-B',str(HERE/'test_walk.py')],check=True,timeout=60)
    path=HERE/'WALK-BOUND.json'
    if args.write_receipt:path.write_text(json.dumps(receipt,indent=2)+'\n')
    else:need(json.loads(path.read_text())==receipt,'minimum-source receipt drift')
    print(f'PASS_CHARGED_SOURCE_WALKS n=9,12 generic=inverse_checked independent_dense={cases} '
          f'omissions={omissions} tests=10 sweep=114 decomposition_counterexample=checked source_count_gap_lt_3percent=checked no_new_kappa')


if __name__=='__main__':main()
