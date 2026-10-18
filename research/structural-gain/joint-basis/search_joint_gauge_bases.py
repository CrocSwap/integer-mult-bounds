#!/usr/bin/env python3
"""Joint donor bases and gauges from dependencies on forbidden output rows.

This is a literal finite experiment with exact rational identities and full
paid frames. Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter,defaultdict
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--selection',type=Path,required=True)
    ap.add_argument('--gk-dir',type=Path,required=True)
    ap.add_argument('--search-code',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();assert __debug__ and not a.out.exists();a.out.mkdir(parents=True)
    sys.path.insert(0,str(a.gk_dir.resolve()));sys.path.insert(0,str(a.search_code.resolve()))
    import gk_word as g,gk_common as co
    from coupled_frames_base import Chains,basis,span,meet,contained
    from promote_cold_frames import ForwardFrames
    from search_suffix_kernels import linear_basis,solve,add
    g.V=co.V=112;g.DATA=co.DATA=7168
    raw=gzip.decompress(a.word.read_bytes());original=json.loads(raw);base=copy.deepcopy(original)
    selection=json.loads(a.selection.read_text());unlocked={p+224 for c in selection['kernel']for p in c['pivots']}
    assert len(unlocked)==44 and all(e[0]=='add'and e[1]>=224 and e[2]>=224 for e in base['A'][:69])
    base['A']=base['A'][69:]
    base['start_extra']={r:E for r,E in base['start_extra'].items()if int(r)not in unlocked}
    base['cleanup']=[g.inverse(e,g.FULL)for e in reversed(base['A']+base['B'])if not 112<=e[1]<224]
    C=g.responses(base);assert all(not C[int(r)-224]for r in base['start_extra'])
    graph=Chains(base);forward=ForwardFrames(base);upper=forward.frames.copy()
    for node in reversed(range(forward.gates)):
        cap=graph.full
        for r in forward.roles[node]:cap=meet(cap,upper[forward.next[node,r]])
        upper[node]=cap
    centers={r:basis(tuple(F))for r,F in zip(base['centers'],base['center_frames'])}
    serving=defaultdict(set)
    for event in base['cut']:serving[event[1]-112].add(event[2])
    target_caps={}
    for t in range(112):
        cap=upper[forward.regs[t+112][0]]
        for r in serving[t]:cap=meet(cap,centers[r])
        target_caps[t]=cap
    cold=[h for h in range(504)if C[h]and str(h+224)not in base['start_extra']]
    helper_caps={h:graph.upper[graph.regs[h+224][1]]for h in cold}
    options=set()
    for cap in helper_caps.values():
        current={()}
        for vector in span(cap)-{0}:current|={basis(E+(vector,))for E in tuple(current)}
        options|=current-{()}
    counts=Counter();found=[];started=time.monotonic();no_gauge=[]
    for E in sorted(options,key=lambda F:(len(F),F)):
        allowed={t for t in range(112)if contained(E,target_caps[t])}
        if not allowed:
            counts['no_compatible_output_frames']+=1;continue
        eligible=[h for h in cold if contained(E,helper_caps[h])]
        if not eligible:continue
        counts['projected_frame_classes']+=1
        projected=[{t:q for t,q in col.items()if t not in allowed}for col in C]
        donors=[];eliminated={};relations={}
        # Prefer donors with small gauge-compatible response support to leave
        # broad-response columns as pivots; every span query is still exact.
        eligible.sort(key=lambda h:(len(C[h]),h))
        for h in eligible:
            rel=solve(projected[h],eliminated)
            if rel is None:
                donors.append(h);eliminated=linear_basis(projected,donors)
            elif all(not(q.denominator&(q.denominator-1))for q in rel.values()):relations[h]=rel
        if not relations:continue
        residuals={}
        for p,rel in relations.items():
            remainder=C[p].copy()
            for d,q in rel.items():add(remainder,C[d],-q)
            assert set(remainder)<=allowed
            residuals[p]=remainder
        gauged=[p for p,col in residuals.items()if col]
        if not gauged:
            counts['dependencies_with_zero_gauge_residual']+=1;no_gauge.append(list(E));continue
        counts['joint_kernel_gauge_classes']+=1
        members=set(relations)|{d for rel in relations.values()for d in rel}
        changed={};Bchanged={};candidate=copy.deepcopy(base);pre=[];targets=set()
        for h in members:
            closure=graph.closure(graph.regs[h+224][1],E,'raise',len(graph.nodes));assert closure is not None
            for node,F in closure.items():changed[node]=basis(changed.get(node,graph.nodes[node]['F'])+F)
        for p,rel in relations.items():
            candidate['start_extra'][str(p+224)]=list(E)
            for d,q in rel.items():pre.append(['add',d+224,p+224,-q.numerator,q.denominator,list(E)])
            for t,q in residuals[p].items():
                pre.append(['add',t+112,p+224,-q.numerator,q.denominator,list(E)]);targets.add(t)
        for t in targets:
            assert forward.raise_frame(Bchanged,forward.regs[t+112][0],E)
            candidate['target_levels'][str(t)]=list(E)
        for node,F in changed.items():
            point=graph.nodes[node];candidate[point['section']][point['index']][-1]=list(F)
        for node,F in Bchanged.items():candidate['B'][node][-1]=list(basis(tuple(candidate['B'][node][-1])+F))
        candidate['A']=pre+candidate['A']
        candidate['cleanup']=[g.inverse(e,g.FULL)for e in reversed(candidate['A']+candidate['B'])if not 112<=e[1]<224]
        try:profile=g.profile(candidate)
        except AssertionError:
            counts['frame_composition_rejected']+=1;continue
        after=g.responses(candidate)
        assert all(not after[int(r)-224]for r in candidate['start_extra'])
        widths=co.widths_of(candidate)
        candidate['report'].update(local_profile=dict(profile),local_rank_mass=sum(r*n for r,n in profile.items()),
                                 width_inventory=dict(Counter(widths)),entrance_rank=sum(9-w for w in widths),
                                 entering_helpers=sum(w<9 for w in widths))
        record=dict(frame=list(E),allowed_targets=sorted(allowed),gauged_pivots=gauged,
                    pure_kernel_pivots=sorted(set(relations)-set(gauged)),donors=sorted(members-set(relations)),
                    relations={str(p):{str(d):str(q)for d,q in rel.items()}for p,rel in relations.items()},
                    gauge_residuals={str(p):{str(t):str(q)for t,q in col.items()}for p,col in residuals.items()if col},
                    changed_helper_frames=len(changed),changed_target_frames=len(Bchanged),
                    profile_after=dict(profile),widths_after=dict(Counter(widths)),
                    all_entering_columns_zero=True,inserted_prefix_gates=len(pre))
        found.append((record,candidate))
    for i,(record,candidate)in enumerate(found):
        folder=a.out/('candidate-%03d'%i);folder.mkdir()
        (folder/'FULL-WORD.json.gz').write_bytes(g.dump(candidate))
        (folder/'CONSTRUCTION.json').write_text(json.dumps(record,indent=2)+'\n')
    report=dict(status='PASS_EXACT_JOINT_KERNEL_GAUGE_BASIS_SCREEN',
                source_content_sha256=hashlib.sha256(raw).hexdigest(),counts=dict(counts),
                subspace_classes=len(options),target_cap_rank_histogram=dict(Counter(map(len,target_caps.values()))),
                target_caps={t:list(F)for t,F in target_caps.items()},candidates=[r for r,_ in found],
                seconds=time.monotonic()-started,
                scope='Jointly unlock44 static pivots. Every eligible entrance subspace tested '
                      'against response rows forbidden by output/center caps. One dyadic donor '
                      'basis per class and all its dependent pivots, with literal shared gauges '
                      'and full paid frames. Multiple nested classes/output-basis changes excluded.')
    (a.out/'SEARCH.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(counts=dict(counts),candidates=len(found),seconds=report['seconds']),indent=2))


if __name__=='__main__':main()
