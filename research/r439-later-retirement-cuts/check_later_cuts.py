# SPDX-License-Identifier: Apache-2.0
"""Independent every-boundary inverse replay; no later_cuts/verify imports."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('integer_geometry',HERE/'independent.py')
I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I)


def check(cert):
    raw=(I.ROOT/I.WORD).read_bytes();I.need(hashlib.sha256(raw).hexdigest()==I.SHA,'source hash')
    w=json.loads(gzip.decompress(raw));n=2*w['v']+w['R'];v=w['v']
    state=[{r} for r in range(n)];current=w['start'][:]
    prefix=w['D']+w['A']+[[0,v+t,[w['ret'][j]]] for t,js in enumerate(w['scatter']) for j in js]
    for section in ['D','A']:
        for f,t,ss in w[section]:
            for r in [t]+ss:current[r]=f
            for s in ss:state[t]^=state[s]
    for t,js in enumerate(w['scatter']):
        for j in js:state[v+t]^=state[w['ret'][j]]
    frames=[I.reduce_rows([w['lines'][i] for i in f]) for f in w['frames']]
    expanded={}
    I.need([h['helper'] for h in cert['helpers']]==[465,466,468,469,470,476],'helper coverage')
    for entry in cert['helpers']:
        sequence=[]
        for run in entry['runs']:
            I.need(run['first_cut']==len(sequence) and run['last_cut']>=run['first_cut'],'run coverage')
            sequence += [run['conditions']]*(run['last_cut']-run['first_cut']+1)
        I.need(len(sequence)==713,'cut coverage')
        passed=[k for k,r in enumerate(sequence) if r.get('lost_targets')==[]]
        windows=[]
        for k in passed:
            if not windows or windows[-1][1]+1!=k:windows.append([k,k])
            else:windows[-1][1]=k
        I.need(windows==entry['windows'] and len(passed)==entry['necessary_condition_pass_count'],'windows')
        I.need(sum(r['joint_rank']==7 for r in sequence)==entry['joint_rank_seven_cuts'],'join counts')
        expanded[entry['helper']]=sequence
    geometry,subset_cache={},{}
    def join(registers):
        key=tuple(sorted({current[r] for r in registers}))
        if key not in geometry:geometry[key]=I.reduce_rows([x for f in key for x in frames[f]])
        return geometry[key]
    def subset(vecs,f):
        key=(tuple(map(tuple,vecs)),f)
        if key not in subset_cache:subset_cache[key]=len(I.reduce_rows(vecs+frames[f]))==len(frames[f])
        return subset_cache[key]
    def support(value):return [r for r in range(n) if value & (1<<r)]
    for k in range(713):
        # Deliberately recompute the entire inverse independently at EACH
        # boundary; never use the primary incremental inverse update.
        inverse=[1<<r for r in range(n)]
        for _,dst,srcs in reversed(prefix+w['B'][:k]):
            for src in srcs:inverse[dst]^=inverse[src]
        for h,sequence in expanded.items():
            donors=support(inverse[h]);dirt=[r for r in range(n) if h in state[r]]
            test=set()
            for r in donors:test^=state[r]
            I.need(test=={h},'direct restoration identity')
            U=join(donors+dirt+[h]);actual={'joint_rank':len(U)}
            if len(U)<=7:
                J=join(donors+[h]);touched=set(donors+[h]);lost=[]
                for t in range(v):
                    if not subset(J,w['final'][v+t]):
                        row=inverse[v+t]^inverse[t]
                        if any(row & (1<<r) for r in touched):lost.append(v+t)
                actual.update(restoration_rank=len(J),lost_targets=lost,restore_donors=donors)
            I.need(actual==sequence[k],f'boundary classification h={h} cut={k}')
        if k<len(w['B']):
            f,t,ss=w['B'][k]
            for r in [t]+ss:current[r]=f
            for s in ss:state[t]^=state[s]
    I.need(cert['cuts_per_helper']==713 and cert['helper_cut_pairs']==4278 and cert['B_gate_count']==712,'coverage metadata')
    I.need(cert['source_sha256']==I.SHA and cert['no_new_kappa'] is True,'source metadata')
    return True

if __name__=='__main__':
    check(json.loads((HERE/'LATER-CUTS.json').read_text()))
    print('PASS_INDEPENDENT_LATER_CUTS full_inverse_rebuilds=713 helper_cut_pairs=4278')
