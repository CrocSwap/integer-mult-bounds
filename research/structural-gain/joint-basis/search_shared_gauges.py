#!/usr/bin/env python3
"""Compose entrance gauges sharing target rises and center descents.

All compatible line/plane classes are determined from exact response support
and maximal legal future frames. Prepared with OpenAI Codex, Apache-2.0.
"""
import argparse
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
    ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--gk-dir',type=Path,required=True)
    ap.add_argument('--search-code',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();assert __debug__ and not a.out.exists();a.out.mkdir(parents=True)
    sys.path.insert(0,str(a.gk_dir.resolve()));sys.path.insert(0,str(a.search_code.resolve()))
    import gk_word as g,gk_common as co
    from coupled_frames_base import Chains,basis,span,meet
    from promote_cold_frames import ForwardFrames
    g.V=co.V=112;g.DATA=co.DATA=7168
    raw=gzip.decompress(a.word.read_bytes());word=json.loads(raw);C=g.responses(word)
    graph=Chains(word);forward=ForwardFrames(word)
    upper=forward.frames.copy()
    for node in reversed(range(forward.gates)):
        cap=graph.full
        for r in forward.roles[node]:cap=meet(cap,upper[forward.next[node,r]])
        upper[node]=cap
    centers={r:basis(tuple(F))for r,F in zip(word['centers'],word['center_frames'])}
    serving=defaultdict(set)
    for event in word['cut']:
        assert event[0]=='add'
        serving[event[1]-112].add(event[2])
    classes=defaultdict(list);caps={};counts=Counter()
    for h,column in enumerate(C):
        r=h+224
        if not column or str(r)in word['start_extra']:continue
        cap=graph.upper[graph.regs[r][1]]
        for t in column:
            cap=meet(cap,upper[forward.regs[t+112][0]])
            for center in serving[t]:cap=meet(cap,centers[center])
        counts['helper_cap_rank'+str(len(cap))]+=1
        caps[r]=list(cap)
        options={()}
        for vector in sorted(span(cap)-{0}):
            options|={basis(E+(vector,))for E in tuple(options)if len(E)<3}
        for frame in options-{()}:classes[frame].append(r)
    original=g.profile(word);found=[]
    for frame,helpers in sorted(classes.items(),key=lambda item:(len(item[0]),item[0])):
        candidate=copy.deepcopy(word);changes={};Bchanges={};gates=[];targets=set()
        for r in helpers:
            closure=graph.closure(graph.regs[r][1],frame,'raise',len(graph.nodes));assert closure is not None
            for node,F in closure.items():changes[node]=basis(changes.get(node,graph.nodes[node]['F'])+F)
            candidate['start_extra'][str(r)]=list(frame)
            for t,coefficient in C[r-224].items():
                q=-coefficient;gates.append(['add',t+112,r,q.numerator,q.denominator,list(frame)])
                targets.add(t)
        for t in targets:
            assert forward.raise_frame(Bchanges,forward.regs[t+112][0],frame)
            candidate['target_levels'][str(t)]=list(frame)
        for node,F in changes.items():
            point=graph.nodes[node];event=candidate[point['section']][point['index']]
            event[-1]=list(basis(tuple(event[-1])+F))
        for node,F in Bchanges.items():candidate['B'][node][-1]=list(basis(tuple(candidate['B'][node][-1])+F))
        candidate['A']=gates+candidate['A']
        candidate['cleanup']=[g.inverse(e,g.FULL)for e in reversed(candidate['A']+candidate['B'])if not 112<=e[1]<224]
        try:profile=g.profile(candidate)
        except AssertionError:
            counts['frame_composition_rejected']+=1;continue
        after=g.responses(candidate)
        assert all(not after[int(r)-224]for r in candidate['start_extra'])
        delta={r:profile[r]-original[r]for r in set(profile)|set(original)if profile[r]!=original[r]}
        widths=co.widths_of(candidate)
        candidate['report'].update(local_profile=dict(profile),local_rank_mass=sum(r*n for r,n in profile.items()),
                                 width_inventory=dict(Counter(widths)),entrance_rank=sum(9-w for w in widths),
                                 entering_helpers=sum(w<9 for w in widths))
        rec=dict(frame=list(frame),helpers=helpers,targets=sorted(targets),added_gates=len(gates),
                 profile_after=dict(profile),profile_delta=delta,widths_after=dict(Counter(widths)),
                 helper_frame_changes=len(changes),target_frame_changes=len(Bchanges),
                 exact_all_entering_response_columns_zero=True)
        found.append((rec,candidate));counts['literal_gauge_compositions']+=1
    for i,(rec,candidate)in enumerate(found):
        folder=a.out/('candidate-%03d'%i);folder.mkdir()
        (folder/'FULL-WORD.json.gz').write_bytes(g.dump(candidate))
        (folder/'CONSTRUCTION.json').write_text(json.dumps(rec,indent=2)+'\n')
    report=dict(status='PASS_EXACT_SHARED_GAUGE_SCREEN',source_content_sha256=hashlib.sha256(raw).hexdigest(),
                counts=dict(counts),helper_caps=caps,classes=len(classes),candidates=[r for r,_ in found],
                scope='Every common line/plane/3-space in the intersection of helper first-future cap, '
                      'all response-supported output caps, and all centers serving those outputs. '
                      'One full eligible-helper group per frame; literal shared target/center costs. '
                      'Alternative output bases, multiple nested gauge frames and subset choices excluded.')
    (a.out/'SEARCH.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(counts=dict(counts),classes=len(classes),candidates=len(found)),indent=2))


if __name__=='__main__':main()
