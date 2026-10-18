"""Complete common-shift k8 triple census. Philipp / GPT-6 Astra, Apache-2.0.

Uses attributed PR1310/1263/1161 source extraction, eligibility, scalar replay
and complete invoice. The common-shift census and its receipts are new.
"""
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import importlib.util
import json
from math import comb
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,message):
    if not ok: raise ValueError(message)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(x): return hashlib.sha256(x).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib);return lib

def sources():
    pins=json.loads((HERE/'PREDECESSORS.json').read_bytes())
    need(pins['pr1310']=='b9ca10f02fca37c8214d880c244ac14ead6bae7a','predecessor head')
    actual={str(p.relative_to(HERE)) for p in (HERE/'vendor').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(set(pins['files'])==actual,'complete vendor inventory')
    for path,digest in pins['files'].items():need(sha((HERE/path).read_bytes())==digest,'source '+path)
    for entry in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
        if entry['usage']!='input':continue
        need(sha((ROOT/entry['path']).read_bytes())==entry['sha256'],'external source '+entry['path'])
    pair=module('credited_pr1310',HERE/'vendor/pr1310/verify.py');pair.ROOT=ROOT
    prior,lib=pair.sources()
    return pair,prior,lib

def f(unit,e): return abs(e)-int(unit and e==0)

def curves(terms,helpers,gauges):
    """Cost changes for singletons and cancellation on internal ADDs."""
    incident={h:Counter() for h in helpers};shared=defaultdict(Counter)
    adjacency={h:set() for h in helpers}
    for unit,e,t,s in terms:
        e+=gauges.get(t,0)-gauges.get(s,0)
        for h,sign in ((t,1),(s,-1)):
            if h in incident:incident[h][unit,e,sign]+=1
        if t in incident and s in incident:
            need(t!=s,'distinct ADD operands')
            adjacency[t].add(s);adjacency[s].add(t)
            shared[tuple(sorted((t,s)))][unit,e]+=1
    # A harmless overestimate of each subset's actual breakpoints, plus zero.
    shifts=sorted({0}|{-gauges.get(h,0) for h in helpers}|
                  {-sign*e for h in helpers for unit,e,sign in incident[h]})
    singles={h:[2*(abs(gauges.get(h,0)+d)-abs(gauges.get(h,0)))+
        sum(n*(f(u,e+sign*d)-f(u,e)) for (u,e,sign),n in incident[h].items())
        for d in shifts] for h in helpers}
    correction={edge:[sum(n*(2*f(u,e)-f(u,e+d)-f(u,e-d)) for (u,e),n in records.items())
        for d in shifts] for edge,records in shared.items()}
    return shifts,singles,correction,adjacency

def census(terms,helpers,gauges):
    shifts,singles,correction,adj=curves(terms,helpers,gauges)
    zero=[0]*len(shifts)
    pair_rows=[]; block_winners=[]
    for h in helpers:
        best=min((singles[h][i],abs(d),d) for i,d in enumerate(shifts))
        if best[0]<0:block_winners.append((best[0],1,(h,),best[1],best[2]))
    for a,b in combinations(helpers,2):
        fix=correction.get((a,b),zero)
        values=[singles[a][i]+singles[b][i]+fix[i] for i in range(len(shifts))]
        best=min((values[i],abs(d),d) for i,d in enumerate(shifts))
        pair_rows.append([a,b,best[0]])
        if best[0]<0:block_winners.append((best[0],2,(a,b),best[1],best[2]))
    # At termination, nonnegative smaller blocks certify disconnected triples.
    triples=sorted({tuple(sorted((h,a,b))) for h in helpers for a,b in combinations(adj[h],2)})
    digest=hashlib.sha256();minima=hashlib.sha256();hist=Counter();wins=[];evaluations=0
    for a,b,c in triples:
        ab=correction.get((a,b),zero);ac=correction.get((a,c),zero);bc=correction.get((b,c),zero)
        values=[singles[a][i]+singles[b][i]+singles[c][i]+ab[i]+ac[i]+bc[i] for i in range(len(shifts))]
        winner=min((values[i],abs(d),d) for i,d in enumerate(shifts))
        digest.update(canonical([a,b,c,values])+b'\n');minima.update(canonical([a,b,c,winner[0]])+b'\n');hist[winner[0]]+=1;evaluations+=len(values)
        if winner[0]<0:
            block_winners.append((winner[0],3,(a,b,c),winner[1],winner[2]))
            wins.append({'helpers':[a,b,c],'shift':winner[2],'delta_real':winner[0],
                'all_improving_shifts':[[d,values[i]] for i,d in enumerate(shifts) if values[i]<0]})
    chosen=min(block_winners) if block_winners else (0,0,(),0,0)
    return {'winner':{'delta_real':chosen[0],'helpers':list(chosen[2]),'shift':chosen[4]},
        'singleton_minimum_histogram':sorted(Counter(min(row) for row in singles.values()).items()),
        'pair_minimum_histogram':sorted(Counter(row[2] for row in pair_rows).items()),
        'shift_breakpoints_superset':shifts,'singletons':len(helpers),'pairs':len(pair_rows),
        'interaction_edges':len(correction),'connected_triples':len(triples),
        'disconnected_triples':comb(len(helpers),3)-len(triples),'all_triples':comb(len(helpers),3),
        'evaluations':evaluations,'single_curves_sha256':sha(canonical(singles)),
        'pair_minima_sha256':sha(canonical(pair_rows)),'triple_curves_sha256':digest.hexdigest(),'triple_minima_sha256':minima.hexdigest(),
        'minimum_histogram':sorted(hist.items()),'improving_triples':wins}

def compute():
    pair,prior,lib=sources();word,programs,*_=lib.load();helpers=prior.domain(lib,word,programs)
    inherited=json.loads((HERE/'vendor/pr1310/CERTIFICATE.json').read_bytes())
    result={'status':'PASS_K8_COHERENT_TRIPLES','seed':37,'base':'bce54fb3f895cbe5cd4c0eb477c3afeed100190f',
            'eligible_helpers':helpers,'orientations':{}}
    for orientation in ('forward','backward'):
        gauges={int(h):k for h,k in inherited['orientations'][orientation]['gauges'].items()}
        terms=prior.terms_from(lib,programs[orientation],helpers)
        before=census(terms,helpers,gauges)
        need(len(before['improving_triples'])==1,'unique coherent improving triple')
        win=before['improving_triples'][0]
        need(win['helpers']==[354,469,478] and win['delta_real']==-2,'witness identity')
        old=prior.transform(lib,word,programs[orientation],gauges)
        newgauges=dict(gauges);trace=[before]
        for _ in range(25):
            win=trace[-1]['winner']
            if win['delta_real']>=0:break
            for h in win['helpers']:
                newgauges[h]=newgauges.get(h,0)+win['shift']
                if newgauges[h]==0:del newgauges[h]
            trace.append(census(terms,helpers,newgauges))
        else:raise ValueError('descent cap reached')
        after=trace[-1]
        need(after['winner']['delta_real']==0,'coherent block closure')
        new=prior.transform(lib,word,programs[orientation],newgauges)
        oldbill=lib.invoice(old,'copy-init');newbill=lib.invoice(new,'copy-init')
        baseline=lib.invoice(programs[orientation],'copy-init')
        need(newbill['real_primitives']-oldbill['real_primitives']==sum(r['winner']['delta_real'] for r in trace),'full real invoice saving')
        need(newbill['paid_profile']==oldbill['paid_profile']==baseline['paid_profile'],'paid profile')
        need([x for x in new if x[0]!='scalar']==[x for x in old if x[0]!='scalar'],'non-scalar events')
        need(lib.replay(old,orientation)==lib.replay(new,orientation),'all formal endpoints')
        result['orientations'][orientation]={'trace':trace,'gauges':newgauges,
            'baseline':baseline,'predecessor':oldbill,'candidate':newbill,'candidate_sha256':sha(canonical(new)),
            'endpoint':lib.replay(new,orientation)}
    return result

def check_certificate(result,expected):need(canonical(result)==canonical(expected),'complete certificate equality')

if __name__=='__main__':
    result=compute();path=HERE/'CERTIFICATE.json'
    if '--write' in sys.argv:
        need(not path.exists(),'refusing overwrite');path.write_bytes(canonical(result)+b'\n')
    else:check_certificate(result,json.loads(path.read_bytes()))
    print(result['status'],'all_triples',result['orientations']['forward']['trace'][0]['all_triples'],
          'unique_improvement',[354,469,478],'complex_saving_per_orientation',result['orientations']['forward']['predecessor']['complex_primitives']-result['orientations']['forward']['candidate']['complex_primitives'],'no_new_kappa')
