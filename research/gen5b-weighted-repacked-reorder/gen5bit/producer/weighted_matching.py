#!/usr/bin/env python3
"""Rebuild donor-rank-weighted reuse after the inherited producer endpoint descent.

Prepared for George Lydakis with substantial OpenAI Codex assistance. Apache-2.0.
Compensated reuse, exact frame classes and the underlying gen5b word are inherited.
"""
import sys
if not __debug__:raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode=True
import argparse,collections,gzip,hashlib,importlib.util,json,shutil,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_WORD='acdd48514bb1b0b1c012f924a2414be9c7a6ef43a6a6ba92b94ab4afdd877003'
FINAL_WORD='9144bc371104df43abf65f8fcff7a0f195301118ccb4c37b02799799d9f2eec1'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True,help='PR200 layout containing bit/, references/ and selected/bit/')
    ap.add_argument('--output',type=Path,required=True,help='New directory for the five regenerated bit files')
    ap.add_argument('--receipt',type=Path,required=True);a=ap.parse_args()
    assert not a.output.exists() and not a.receipt.exists()
    start=time.monotonic();source=a.source/'selected/bit'
    assert hashlib.sha256(gzip.decompress((source/'word_p12.json.gz').read_bytes())).hexdigest()==BASE_WORD
    W=load('weighted_matching_word',a.source/'bit/word.py').Candidate();C=W.C
    W.exact_frames();baseline=W.row();assert len(W.pairs)==1726
    gauges=W.gauge;chain=collections.defaultdict(list)
    for b in W.order:
        for t in gauges[b]['targets']:chain[t].append(b)
    successors=collections.defaultdict(set)
    for rows in chain.values():
        groups=[]
        for b in rows:
            f=gauges[b]['frame']
            if groups and C.sub(f,gauges[groups[-1][0]]['frame']) and C.sub(gauges[groups[-1][0]]['frame'],f):groups[-1].append(b)
            else:groups.append([b])
        for left,right in zip(groups,groups[1:]):
            for b in left:successors[b].update(right)
    times={b:W.first[b]for b in gauges};assert min(times.values())>=0
    for b in reversed(W.order):
        for c in successors[b]:times[b]=min(times[b],times[c])
    assert all(times[b]<=times[c]for b,cs in successors.items()for c in cs)
    previous={}
    for b in sorted(W.order,key=lambda b:times[b]):
        for t in gauges[b]['targets']:
            if t in previous:assert C.sub(previous[t],gauges[b]['frame'])
            previous[t]=gauges[b]['frame']
    byframe=collections.defaultdict(list)
    for d in range(W.R):
        if d not in gauges and d not in W.rootroles and d not in W.source.values() and d in W.role_ops:
            if C.nondeg(W.endframe[d]):byframe[W.endframe[d]].append(d)
    recipients=list(W.order);adj=[];edge_ranks=collections.Counter();nd={}
    for b in recipients:
        f=gauges[b]['frame'];edges=[]
        if f not in nd:nd[f]=C.nondeg(f)
        if nd[f]:
            for g,donors in byframe.items():
                if C.dimf[g]>C.dimf[f]:continue
                available=[d for d in donors if W.last[d]<times[b]]
                if available and C.sub(g,f):edges.extend(available)
        adj.append(edges);edge_ranks[gauges[b]['dim']]+=len(edges)
    assert sum(map(len,adj))==65920
    reverse=collections.defaultdict(list)
    for i,donors in enumerate(adj):
        assert not donors or gauges[recipients[i]]['dim']==21
        for d in donors:reverse[d].append(i)
    # Donor sets form a transversal matroid; rank orders donor-only benefit
    # (24-e)^p-(21-e)^p for every fixed 0<p<1. This does not optimize later stages.
    assigned={};sys.setrecursionlimit(20000)
    def insert(d,seen):
        for i in reverse[d]:
            if i in seen:continue
            seen.add(i)
            if i not in assigned or insert(assigned[i],seen):assigned[i]=d;return True
        return False
    for d in sorted(reverse,key=lambda d:(-C.dimf[W.endframe[d]],d)):insert(d,set())
    matching=load('weighted_matching_hopcroft_karp',HERE/'make_physical.py')
    assert len(assigned)==1728==sum(x>=0 for x in matching.hopcroft_karp(adj,len(recipients)))
    pairs=[[assigned[i],b]for i,b in enumerate(recipients)if i in assigned]
    result=dict(source='PR299 5f6bd3fbc0e6796dd31263cef1f06dc968186f64, inherited PR296 gen5b producer',
        input_word_sha256=BASE_WORD,baseline_pairs=1726,candidate_pairs=len(pairs),edge_count=sum(map(len,adj)),
        recipient_edges_by_rank=dict(edge_ranks),baseline_donor_end_ranks=dict(collections.Counter(C.dimf[W.endframe[d]]for b,d in W.pairs)),
        candidate_donor_end_ranks=dict(collections.Counter(C.dimf[W.endframe[d]]for d,b in pairs)),pairs=pairs,readtimes=times,baseline_row=baseline)
    W.pairs=[[b,d]for d,b in pairs];W.donor=dict(W.pairs);W.phys={s:W.donor.get(s,s)for s in range(W.R)}
    W.readtime=dict(W.readtime)
    for d,b in pairs:W.readtime[b]=times[b]
    W.w['pairs']=pairs;W.w['reads']={str(b):len(W.phase1)+W.readtime[b]for b in W.order if W.readtime[b]}
    W.exact_frames();result['exact_row']=W.row();result['formal']=[W.formal(r)for r in(2,0)]
    assert result['formal'][0]['identity']
    assert all(x['defining_decoder']and x['all_dirty_and_source_columns_restored']for x in result['formal'])
    raw=(json.dumps(W.w,sort_keys=True)+'\n').encode();assert hashlib.sha256(raw).hexdigest()==FINAL_WORD
    a.output.mkdir(parents=True)
    for name in('graph_p12.json','profile_p12.json','kchron_p12.json','frames_p12.json.gz'):shutil.copyfile(source/name,a.output/name)
    (a.output/'word_p12.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    result.update(status='PASS_REGENERATED_WEIGHTED_MATCHING_AND_ALL_LOCAL_COLUMNS',word_sha256=FINAL_WORD,seconds=time.monotonic()-start,
        scope='Maximum-cardinality donor-rank matching in the fixed exact graph; later stages and finite admission require verify.py.')
    a.receipt.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS weighted matching: 1728 pairs, all local columns, word '+FINAL_WORD,flush=True)
if __name__=='__main__':main()
