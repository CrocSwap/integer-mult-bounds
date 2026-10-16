"""Independently rebuild all pre-transcript physical dimension paths from inert data."""
import json
from pathlib import Path
from collections import Counter,defaultdict
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import support
P=support.out('matching','placeholder').parent;support.materialize_word()
g=support.read('bitword/selected/bit/graph_p10.json');F=support.read('bitword/selected/bit/frames_p10.json.gz')['frames'];K=support.read('bitword/selected/bit/kchron_p10.json')
def dim(f):return F[str(f)]['dim']
def summarize(w):
    ga={e['role']:e for e in w['gauges']};source={r:int(n) for n,r in w['sources'].items()}
    pair=dict(w['pairs']);recips=set(pair.values());roles=sorted(set(range(9120))-recips)
    opseq=defaultdict(list);rootseq=defaultdict(list)
    ph=sorted(w['phase1']);phs=set(ph);order=ph+[i for i in range(len(w['ops'])) if i not in phs]
    for i in order:
        for r in w['ops'][i][:2]:opseq[r].append(w['op_frame'][i])
    for r,f in zip(w['rootroles'],w['root_frame']):rootseq[r].append(f)
    def path(dims):
        ans=Counter()
        for a,b in zip(dims,dims[1:]):
            assert a<=b,(a,b,dims)
            if a<b:ans[b-a]+=1
        return ans
    internal=Counter();residual=Counter()
    for r in roles:
        start=dim(ga[r]['frame']) if r in ga else dim(w['source_frame'][source[r]]) if r in source else 0
        trail=[start]+[dim(f) for f in opseq[r]+rootseq[r]]
        if r in pair:
            q=pair[r];trail += [dim(ga[q]['frame'])]+[dim(f) for f in opseq[q]+rootseq[q]]
        trail.append(20);internal.update(path(trail))
        if r in source:internal[1]+=1
        residual[20-(dim(ga[r]['frame']) if r in ga else 0)]+=1
    for j,r in enumerate(g['roots']):
        if r['kind']=='center':internal[dim(w['root_frame'][j])]+=1
    sources=Counter()
    for e in K['entries']:
        sources.update(path([dim(f) for f in e['carrier_chain']]))
        sources.update(path([dim(f) for f in e['passive_chain']]))
    target_paths=[[0] for _ in range(960)]
    reverse=list(reversed(w['gauges']))
    for _,e in sorted(enumerate(reverse),key=lambda x:(w['reads'].get(str(x[1]['role']),len(ph)),x[0])):
        for t in e['targets']:target_paths[t].append(dim(e['frame']))
    deliveries=defaultdict(list)
    for e in K['entries']:deliveries[e['deliver_after_root']].append(e)
    for j,r in enumerate(g['roots']):
        if r['kind']=='side':
            for t in r['targets']:target_paths[t].append(dim(w['root_frame'][j]))
        for e in deliveries[j]:
            for t in e['receivers']:target_paths[t].append(dim(e['deliver_frame']))
    targets=Counter()
    for trail in target_paths:targets.update(path(trail+[19]))
    helper=internal+sources+targets
    paid=Counter({r:5*n for r,n in helper.items()});paid.update({r:1920 for r in (38,19,42,4)})
    return dict(internal=dict(sorted(internal.items())),source=dict(sorted(sources.items())),target=dict(sorted(targets.items())),helper=dict(sorted(helper.items())),
       helper_mass=sum(r*n for r,n in helper.items()),banked_paid=dict(sorted(paid.items())),banked_mass=sum(r*n for r,n in paid.items()),residual_families=dict(sorted(residual.items())),residual_width=sum(r*n for r,n in residual.items()),physical_roles=len(roles))
old=summarize(support.read('bitword/selected/bit/word_p10.json.gz'));new=summarize(json.loads((P/'word_weighted892.json').read_text()))
def delta(a,b):return {r:b.get(r,0)-a.get(r,0) for r in sorted(set(a)|set(b)) if b.get(r,0)!=a.get(r,0)}
out=dict(old=old,new=new,helper_delta=delta(old['helper'],new['helper']),banked_paid_delta=delta(old['banked_paid'],new['banked_paid']),residual_delta=delta(old['residual_families'],new['residual_families']),physical_role_delta=new['physical_roles']-old['physical_roles'],residual_width_delta=new['residual_width']-old['residual_width'],scope='Exact pre-transcript dimension-path census only. Installed stages must be rebound; no supplier moment or full admission claimed.')
assert old['helper_mass']==181050 and new['helper_mass']==181044
assert old['source']==new['source'] and old['target']==new['target']
assert out['helper_delta']=={int(k):v for k,v in json.loads((support.HERE/'witnesses/weighted892-delta.json').read_text())['matching_local_histogram_delta'].items()}
(P/'full_path_census892.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('old','new')},sort_keys=True))
