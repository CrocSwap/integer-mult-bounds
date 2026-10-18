#!/usr/bin/env python3
"""Price every rank-one/rank-two choice on eight independent suffix pairs.

Full shared frame chains are evaluated, not sums of single-move costs.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from bisect import bisect_left
from collections import Counter,defaultdict
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base',type=Path,required=True)
    ap.add_argument('--rank1-word',type=Path,required=True)
    ap.add_argument('--rank2-screen',type=Path,required=True)
    ap.add_argument('--gk-dir',type=Path,required=True)
    ap.add_argument('--search-code',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();assert __debug__ and not a.out.exists();a.out.mkdir(parents=True)
    sys.path.insert(0,str(a.gk_dir.resolve()));sys.path.insert(0,str(a.search_code.resolve()))
    import gk_word as g,gk_common as co
    from promote_cold_frames import ForwardFrames
    from search_suffix_kernels import basis
    g.V=co.V=112;g.DATA=co.DATA=7168
    base=json.loads(gzip.decompress(a.base.read_bytes()));old=json.loads(gzip.decompress(a.rank1_word.read_bytes()))
    rank2=json.loads(a.rank2_screen.read_text())['candidates']
    pivots=sorted(set(map(int,old['start_extra']))-set(map(int,base['start_extra'])))
    assert len(pivots)==8
    rank1={p:dict(pivot=p,frame=old['start_extra'][str(p)],gates=[])for p in pivots}
    index=0
    for event in old['B']:
        if index<len(base['B'])and event[:-1]==base['B'][index][:-1]:index+=1
        else:
            assert event[0]=='add'and event[2]in rank1
            rank1[event[2]]['gates'].append(dict(index=index,donor=event[1],coefficient=str(-Q(event[3],event[4]))))
    assert index==len(base['B'])
    graph=ForwardFrames(base);options={}
    for p in pivots:
        options[p]=[rank1[p],next(r for r in rank2 if r['pivot']==p)]
        for rec in options[p]:
            changed={};frame=basis(tuple(rec['frame']))
            assert graph.raise_frame(changed,graph.regs[p][0],frame)
            for gate in rec['gates']:
                d,i=gate['donor'],gate['index'];node=graph.regs[d][bisect_left(graph.regs[d],i)]
                assert graph.raise_frame(changed,node,frame)
            rec['changes']=changed
    b=.00160337695754026285
    costs={r:r*math.expm1(b*math.log(73/r))/b for r in range(1,10)}
    shadows={4:-7.734887784713593,5:-9.567009138574441,7:-5.83661301196174,
             8:-3.9714149486553896,9:-2.1062168853490393}
    counts=Counter();found=[]
    for mask in range(1<<len(pivots)):
        word=copy.deepcopy(base);inserted=defaultdict(list)
        for j,p in enumerate(pivots):
            rec=options[p][mask>>j&1];frame=rec['frame'];word['start_extra'][str(p)]=frame
            for node,F in rec['changes'].items():
                word['B'][node][-1]=list(basis(tuple(word['B'][node][-1])+F))
            for gate in rec['gates']:
                q=-Q(gate['coefficient'])
                inserted[gate['index']].append(['add',gate['donor'],p,q.numerator,q.denominator,frame])
        for i in sorted(inserted,reverse=True):
            word['B'][i:i]=sorted(inserted[i],key=lambda e:(len(e[-1]),e[-1],e[2],e[1]))
        counts['compositions']+=1
        try:profile=g.profile(word)
        except AssertionError:
            counts['incompatible_composed_frames']+=1;continue
        word['cleanup']=[g.inverse(e,g.FULL)for e in reversed(word['A']+word['B'])if not 112<=e[1]<224]
        C=g.responses(word)
        assert all(not C[int(r)-224]for r in word['start_extra'])
        counts['exact_compositions']+=1
        widths=co.widths_of(word)
        cost=sum(costs[r]*n for r,n in profile.items())+sum(shadows[w]for w in widths)
        word['report'].update(local_profile=dict(profile),local_rank_mass=sum(r*n for r,n in profile.items()),
                             width_inventory=dict(Counter(widths)),entrance_rank=sum(9-w for w in widths),
                             entering_helpers=sum(w<9 for w in widths))
        rec=dict(mask=mask,rank2_pivots=[p for j,p in enumerate(pivots)if mask>>j&1],
                 profile_after=dict(profile),widths_after=dict(Counter(widths)),floating_dual_cost=cost,
                 exact_all_entering_responses_zero=True)
        found.append((rec,word))
    found.sort(key=lambda pair:pair[0]['floating_dual_cost'])
    for i,(rec,word)in enumerate(found[:8]):
        folder=a.out/('candidate-%03d'%i);folder.mkdir()
        (folder/'FULL-WORD.json.gz').write_bytes(g.dump(word))
        (folder/'CONSTRUCTION.json').write_text(json.dumps(rec,indent=2)+'\n')
    report=dict(status='PASS_EXACT_SHARED_MULTICUT_COMPOSITIONS',
                input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in
                              (a.base,a.rank1_word,a.rank2_screen,Path(__file__))},
                counts=dict(counts),candidates=[rec for rec,_ in found],
                scope='All256 choices between the retained rank-one and discovered rank-two '
                      'circuit for each of eight original suffix pivots. Actual shared frame '
                      'joins and every entering response checked. Opposite-pivot orientations, '
                      'alternative donor bases, gauge changes and native/global admission separate.')
    (a.out/'SEARCH.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(counts=dict(counts),best=found[0][0]if found else None),indent=2))


if __name__=='__main__':main()
