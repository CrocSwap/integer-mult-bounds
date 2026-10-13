#!/usr/bin/env python3
"""Exact circuits over donor/time states, including output target donors.

Unlike a single-cut response basis, distinct epochs of one donor may supply
different columns. Every chosen insertion and shared forward frame climb is
realized literally and repriced. Prepared with OpenAI Codex, Apache-2.0.
"""
import argparse
from bisect import bisect_left
from collections import Counter, defaultdict
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
    ap.add_argument('--gk-dir',type=Path,required=True)
    ap.add_argument('--search-code',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--rank',type=int,choices=(1,2,3),default=2)
    ap.add_argument('--raise-frames',action='store_true')
    ap.add_argument('--retain',type=int,default=30)
    a=ap.parse_args();assert __debug__ and not a.out.exists();a.out.mkdir(parents=True)
    sys.path.insert(0,str(a.gk_dir.resolve()));sys.path.insert(0,str(a.search_code.resolve()))
    import gk_word as g
    import gk_common as co
    from search_suffix_kernels import basis,span,inside,add,frames,linear_basis,solve
    from promote_cold_frames import ForwardFrames
    g.V=co.V=112;g.DATA=co.DATA=7168
    raw=gzip.decompress(a.word.read_bytes());word=json.loads(raw);original=g.profile(word)
    first,before,after=frames(word);graph=ForwardFrames(word)
    full=basis(tuple(1<<i for i in range(9)));upper=graph.frames.copy()
    for node in reversed(range(graph.gates)):
        cap=full
        for r in graph.roles[node]:cap=basis(tuple(sorted(span(cap)&span(upper[graph.next[node,r]]))))
        assert inside(graph.frames[node],cap);upper[node]=cap
    pivots={r:data for r,data in first.items()if r>=224 and str(r)not in word['start_extra'] and data[0]=='B'}
    epochs=defaultdict(list)
    for r in range(728):
        epochs[0].append(r)
        for index in graph.regs[r]:
            if index+1<graph.gates:epochs[index+1].append(r)
    columns=[{}for _ in range(728)]
    for t in range(112):columns[t+112]={t:Q(1)}
    states=[];pivot_columns={}
    for index in reversed(range(graph.gates)):
        event=word['B'][index]
        if event[0]=='add':add(columns[event[2]],columns[event[1]],Q(event[3],event[4]))
        else:columns[event[1]]={t:q*Q(event[2],event[3])for t,q in columns[event[1]].items()}
        for donor in epochs.get(index,[]):
            if not columns[donor]:continue
            following=graph.regs[donor][bisect_left(graph.regs[donor],index)]
            states.append(dict(donor=donor,index=index,node=following,current=before[index][donor],
                               following=graph.frames[following],upper=upper[following],
                               column=columns[donor].copy()))
        for pivot,data in pivots.items():
            if index==data[1]:pivot_columns[pivot]=columns[pivot].copy()
    state_columns=[state['column']for state in states]
    counts=Counter();results=[];start=time.monotonic()
    b=.00160337695754026285
    import math
    costs={r:r*math.expm1(b*math.log(73/r))/b for r in range(1,10)}
    for pivot,(_,first_index,first_frame)in sorted(pivots.items()):
        cap=upper[graph.regs[pivot][0]]if a.raise_frames else first_frame
        options={()}
        for vector in sorted(span(cap)-{0}):
            options|={basis(frame+(vector,))for frame in tuple(options)if len(frame)<a.rank}
        options=sorted(frame for frame in options if len(frame)==a.rank)
        for frame in options:
            eligible=[i for i,s in enumerate(states)if s['donor']!=pivot and s['index']<=first_index
                      and inside(s['current'],frame) and inside(frame,s['upper']if a.raise_frames else s['following'])]
            counts['exact_response_basis_queries']+=1
            def score(i):
                s=states[i];low,high=len(s['current']),len(s['following']);rank=len(frame)
                # Discovery ordering only; the completed shared chain is repriced.
                if inside(frame,s['following']):
                    return ((costs.get(rank-low,0)+costs.get(high-rank,0)-costs.get(high-low,0)),s['index'],s['donor'])
                change={};assert graph.raise_frame(change,s['node'],frame)
                return (100+len(change),s['index'],s['donor'])
            eligible.sort(key=score)
            relation=solve(pivot_columns[pivot],linear_basis(state_columns,eligible))
            if relation is None:continue
            counts['exact_relations']+=1
            if any(q.denominator&(q.denominator-1)for q in relation.values()):
                counts['non_dyadic_relations']+=1;continue
            changed={}
            assert graph.raise_frame(changed,graph.regs[pivot][0],frame)
            for i in relation:assert graph.raise_frame(changed,states[i]['node'],frame)
            candidate=copy.deepcopy(word)
            for index,value in changed.items():candidate['B'][index][-1]=list(value)
            inserted=defaultdict(list)
            recipe=[]
            for i,q in sorted(relation.items(),key=lambda kv:(states[kv[0]]['index'],states[kv[0]]['donor'])):
                s=states[i];inserted[s['index']].append(['add',s['donor'],pivot,-q.numerator,q.denominator,list(frame)])
                recipe.append(dict(index=s['index'],donor=s['donor'],coefficient=str(q)))
            for index in sorted(inserted,reverse=True):candidate['B'][index:index]=inserted[index]
            candidate['start_extra'][str(pivot)]=list(frame)
            candidate['cleanup']=[g.inverse(e,g.FULL)for e in reversed(candidate['A']+candidate['B'])if not 112<=e[1]<224]
            try:profile=g.profile(candidate)
            except AssertionError:
                counts['frame_composition_rejections']+=1;continue
            actual_columns=g.responses(candidate)
            if any(actual_columns[int(r)-224]for r in candidate['start_extra']):
                counts['scalar_composition_rejections']+=1;continue
            delta={r:profile[r]-original[r]for r in set(profile)|set(original)if profile[r]!=original[r]}
            assert sum(r*n for r,n in delta.items())==-a.rank
            widths=co.widths_of(candidate)
            candidate['report'].update(local_profile=dict(profile),local_rank_mass=sum(r*n for r,n in profile.items()),
                                      entrance_rank=sum(9-w for w in widths),entering_helpers=sum(w<9 for w in widths),
                                      width_inventory=dict(Counter(widths)))
            record=dict(pivot=pivot,frame=list(frame),gates=recipe,profile_after=dict(profile),
                        profile_delta=delta,widths_after=dict(Counter(widths)),changed_existing_gates=len(changed),
                        added_gates=len(recipe),discovery_local_cost=sum(costs[r]*n for r,n in delta.items()),
                        exact_entering_response_columns_zero=True)
            results.append((record,candidate));counts['literal_candidates']+=1
        print(json.dumps(dict(pivot=pivot,frames=len(options),counts=dict(counts),seconds=time.monotonic()-start)),flush=True)
    results.sort(key=lambda pair:(pair[0]['discovery_local_cost'],pair[0]['added_gates']))
    for i,(record,candidate)in enumerate(results[:a.retain]):
        folder=a.out/('candidate-%03d'%i);folder.mkdir()
        (folder/'FULL-WORD.json.gz').write_bytes(g.dump(candidate))
        (folder/'CONSTRUCTION.json').write_text(json.dumps(record,indent=2)+'\n')
    report=dict(status='PASS_EXACT_MULTICUT_RESPONSE_BASIS_SCREEN',
                source_content_sha256=hashlib.sha256(raw).hexdigest(),rank=a.rank,raise_frames=a.raise_frames,
                donor_epoch_states=len(states),pivots=len(pivots),counts=dict(counts),
                candidates=[r for r,_ in results],seconds=time.monotonic()-start,
                scope='All compatible donor epochs, including post-scatter target donors, before '
                      'each previously untouched pivot first use; one cost-ordered rational basis. '
                      'Literal shared frame closure and all entering response columns checked. '
                      'Native exact scalar replay, phases and global admission remain separate.')
    (a.out/'SEARCH.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(counts=dict(counts),best=results[0][0]if results else None),indent=2))


if __name__=='__main__':main()
