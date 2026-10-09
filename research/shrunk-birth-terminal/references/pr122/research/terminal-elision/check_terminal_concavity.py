#!/usr/bin/env python3
"""Independent exact linkage of terminal-elision packets and full profiles."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--case',type=Path,required=True);p.add_argument('--audit',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    w=json.loads(gzip.decompress((a.parent/'word.json.gz').read_bytes()))
    e=json.loads(gzip.decompress((a.case/'word.json.gz').read_bytes()))
    old=json.loads((a.parent/'complex-profile.json').read_text());new=json.loads((a.case/'complex-profile.json').read_text())
    audit=json.loads((a.audit/'receipt.json').read_text())
    assert audit['actual_full_profile_reconstructed'] and audit['all_input_dirty_identity']
    h,v=w['h'],w['v'];m=h*h;M=[0]*v
    for s in w['deferred']:
        for t in w['reach'][s]:M[t]=max(M[t],len(w['sigma'][str(s)]))
    formula=Counter();targets=set();packet_types=Counter()
    for s in e['removed']:
        j=w['role_root'][str(s)];t=w['target'][j]
        assert t not in targets and not w['kind'][j];targets.add(t)
        sig=len(w['sigma'][str(s)]);first=len(w['frames'][str(w['first_node'][s])])
        assert 0<=sig<=M[t]<=first<=h-1
        before=[m-h+sig,1,first-sig,h-1-M[t]];after=[m,first-M[t],0,0]
        assert sum(before)==sum(after) and max(before)<m
        assert all(sum(sorted(after,reverse=True)[:k])>=sum(sorted(before,reverse=True)[:k]) for k in range(1,5))
        for t in before:
            if t:formula[t]-=2*v
        for t in after:
            if t:formula[t]+=2*v
        packet_types[sig,M[w['target'][j]],first]+=1
    actual=Counter({int(t):c for t,c in new['child_multiplicities'].items()})
    actual.subtract({int(t):c for t,c in old['child_multiplicities'].items()})
    actual[m]+=old['W']-new['W']
    assert all(actual[t]==formula[t] for t in actual.keys()|formula.keys())
    assert sum(t*c for t,c in actual.items())==0
    hinges=[sum(min(t,k)*c for t,c in actual.items()) for k in range(1,m+1)]
    assert max(hinges)==0 and min(hinges)<0
    # Exhaustive small parameter controls for the general packet lemma.
    checked=0
    for hh in range(2,17):
        mm=hh*hh
        for sig in range(hh):
            for MM in range(sig,hh):
                for f in range(MM,hh):
                    B=[mm-hh+sig,1,f-sig,hh-1-MM];A=[mm,f-MM,0,0]
                    assert sum(A)==sum(B) and max(B)<mm
                    assert all(sum(sorted(A,reverse=True)[:k])>=sum(sorted(B,reverse=True)[:k]) for k in range(1,5))
                    checked+=1
    a.output.write_text(json.dumps(dict(status='PASS independent exact all-concave terminal gain',roles=len(e['removed']),
        packet_types={str(k):c for k,c in sorted(packet_types.items())},hinge_min=min(hinges),hinge_max=max(hinges),
        full_augmented_delta={t:c for t,c in sorted(actual.items()) if c},small_parameter_cases=checked,
        theorem='For h>=2 and 0<=sigma<=M<=F<=h-1, [h^2,F-M,0,0] strictly majorizes [h^2-h+sigma,1,F-sigma,h-1-M]. Hence the physically verified distinct-target elimination strictly decreases sum(child^p)-W*(h^2)^p for every 0<p<1.'),indent=2)+'\n')
    print('PASS exact full-profile linkage, all concave powers,',checked,'parameter controls')


if __name__=='__main__':main()
