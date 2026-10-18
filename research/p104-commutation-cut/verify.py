#!/usr/bin/env python3
"""Read-only exact replay; standard library, no predecessor executable imports.

Jeremy Diviney with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib,heapq,importlib.util,itertools,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,why):
    if not ok:raise ValueError(why)

def load(name):
    spec=importlib.util.spec_from_file_location('p104_commutation_'+name,HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def scalar(w,ports):
    names=list(w['initial_frames']);rows={s:{s:Q(1)} for s in names}
    paid=Counter()
    for e in w['program']:
        op,t=e[:2]
        if op=='transport':paid[e[4]]+=1
        elif op=='zero':need(t not in rows,'private birth');rows[t]={}
        elif op=='erase':del rows[t]
        elif op=='copy':need(not rows[t],'owned zero copy');rows[t]=rows[e[2]].copy()
        else:
            need(op=='add','event type');_,t,s,a,_=e
            for k,v in list(rows[s].items()):
                new=rows[t].get(k,Q(0))+Q(a)*v
                if new:rows[t][k]=new
                else:rows[t].pop(k,None)
    need(set(rows)==set(names),'private lifetimes closed')
    for s in names:
        expected={s:Q(1)}
        if s.startswith('Y'):
            i=int(s[1:])
            for j,p in enumerate(ports):
                value=Q(sum(a*b for a,b in zip(ports[i],p)),8)
                if value:expected['X'+str(j)]=value
        need(rows[s]==expected,'arbitrary-input scalar endpoint '+s)
    return dict(sorted(paid.items()))

def port_data(fixture):
    lines=set()
    for i,j in itertools.combinations(range(8),2):
        for sign in (-1,1):
            a=[0]*8;a[i]=2;a[j]=2*sign;lines.add(tuple(a))
    for signs in itertools.product((-1,1),repeat=7):
        if signs.count(-1)%2==0:lines.add((1,*signs))
    need(len(lines)==120,'root count')
    cut={tuple(x) for x in fixture['C']+fixture['F0']}
    need(len(cut)==16 and cut<=lines,'puncture')
    ports=sorted(lines-cut);need(len(ports)==104,'ports')
    gram=[[sum(a*b for a,b in zip(u,v))//4 for v in ports] for u in ports]
    need(all(sum(gram[i][k]*gram[k][j] for k in range(104))==26*gram[i][j]
             for i in range(104) for j in range(104)),'G squared = 26G')
    need(sum(gram[i][i] for i in range(104))==208,'trace G = 208')
    return ports

def reachable(graph,extra=()):
    adj=list(graph['adjacency'])
    for a,b in extra:adj[a]|=1<<b
    seen=sum(1<<n for r,n in graph['input_nodes'].items() if r.startswith('X'))
    pending=seen
    while pending:
        bit=pending&-pending;pending^=bit;n=bit.bit_length()-1
        new=adj[n]&~seen;seen|=new;pending|=new
    return sorted(r for r,n in graph['output_nodes'].items() if r.startswith('Y') and seen&(1<<n))

def retime(program):
    last={};children=[[] for _ in program];degree=[]
    for j,e in enumerate(program):
        touched=e[1:3] if e[0] in ('add','copy') else e[1:2]
        ps={last[r] for r in touched if r in last};degree.append(len(ps))
        for p in ps:children[p].append(j)
        for r in touched:last[r]=j
    priority=[hashlib.sha256(('retime-104:'+str(j)).encode()).digest() for j in range(len(program))]
    queue=[(priority[j],j) for j,d in enumerate(degree) if not d];heapq.heapify(queue);result=[]
    while queue:
        _,j=heapq.heappop(queue);result.append(j)
        for k in children[j]:
            degree[k]-=1
            if degree[k]==0:heapq.heappush(queue,(priority[k],k))
    need(len(result)==len(program),'topological retiming')
    need(sum(i!=j for i,j in enumerate(result))>100,'nontrivial retiming')
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for item in pins['files']:
        if item['usage']=='input':need(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'input pin '+item['path'])
    graph_module=load('graph');other=load('independent')
    w=json.loads((graph_module.BASE/'inputs/LOWRANK-WITNESS.json').read_bytes())
    fixture=json.loads((graph_module.BASE/'inputs/P104-FIXTURE.json').read_bytes())['section4_explicit_P104']
    ports=port_data(fixture);paid=scalar(w,ports)
    baseline=json.loads((graph_module.BASE/'inputs/LOWRANK-RESULT.json').read_text())
    need(paid=={int(k):v for k,v in baseline['paid_profile'].items()},'exact baseline profile')
    # Discard every original scalar instruction and its cross-role dependency.
    # Each retained event touches only one role. This permits arbitrary scalar
    # resynthesis and arbitrary interleaving of the fixed transport chains.
    skeleton=dict(w,program=[e for e in w['program'] if e[0] not in ('add','copy')])
    g=graph_module.build();ind=other.check(skeleton)
    need(not g['reached_targets'] and len(g['removed_edges'])==8,'eight-edge union cut')
    primary={'nodes':len(g['nodes']),'frames':len({n[3] for n in g['nodes']}),
             'causal_edges':g['causal_edges'],'potential_common_frame_edges':g['potential_common_frame_edges'],
             'cut_events':[e[0] for e in g['removed_edges']],'cut_ranks':[e[3] for e in g['removed_edges']],
             'reachable_nodes':int(g['reachable_mask_hex'],16).bit_count(),
             'single_edge_reopened_targets':[]}
    for _,a,b,_ in g['removed_edges']:
        targets=reachable(g,[(a,b)]);need(targets,'restore one descent');primary['single_edge_reopened_targets'].append(len(targets))
    need(primary==ind,'two independent graph constructions')
    need(len(reachable(g,[(a,b) for _,a,b,_ in g['removed_edges']]))==104,'intact graph reaches all targets')
    bypass=(g['input_nodes']['X0'],g['output_nodes']['Y0'])
    need('Y0' in reachable(g,[bypass]),'deliberate cross-frame bypass control')
    order=retime(w['program']);rw=dict(w,program=[w['program'][i] for i in order]);need(scalar(rw,ports)==paid,'retimed all-column endpoint')
    retimed=other.check(dict(rw,program=[e for e in rw['program'] if e[0] not in ('add','copy')]))
    for k in ('nodes','frames','causal_edges','potential_common_frame_edges','reachable_nodes'):
        need(retimed[k]==ind[k],'retimed graph invariant '+k)
    controls=[]
    for at in (0,len(w['program'])-1):
        bad=json.loads(json.dumps(w));need(bad['program'][at][0]=='add','endpoint-control cut');bad['program'][at][3]='0'
        try:scalar(bad,ports)
        except ValueError:controls.append('omitted compensation/cleanup at '+str(at))
        else:raise ValueError('endpoint mutation survived')
    bw=json.loads(json.dumps(w))
    for f in list(bw['initial_frames'].values())+list(bw['final_frames'].values()):f.reverse()
    for e in bw['program']:
        if e[0]=='transport':e[2].reverse();e[3].reverse()
        else:e[-1].reverse()
    need(other.check(dict(bw,program=[e for e in bw['program'] if e[0] not in ('add','copy')]))==ind,'frame basis order invariant')
    need(graph_module.build(force_overlap=True)['adjacency']==g['adjacency'],
         'all cross-role equal-frame intervals may overlap in this relaxed skeleton')
    result={'status':'PASS_P104_ALL_COMMUTATIONS_CUT','source_witness_sha256':g['source_witness_sha256'],
            'original_events':len(w['program']),'formal_columns':len(w['initial_frames']),
            'transport_lifetime_events':len(skeleton['program']),
            'removed_original_scalar_events':len(w['program'])-len(skeleton['program']),
            'cut_original_event_indices':[g['retained_event_indices'][e[0]] for e in g['removed_edges']],
            'graph':primary,'original_transfer_rank':8,'required_identity_rank':104,
            'paid_profile':{str(k):v for k,v in paid.items()},'rank_mass':sum(r*c for r,c in paid.items()),
            'retimed_events_moved':sum(i!=j for i,j in enumerate(order)),
            'retimed_order_sha256':hashlib.sha256(json.dumps(order,separators=(',',':')).encode()).hexdigest(),
            'controls':{'single_descent_restorations':8,'cross_frame_bypass':True,
                        'intact_graph':True,'scalar_mutations':controls,'basis_invariance':True,
                        'nontrivial_retiming':True,'all_cross_role_overlaps_granted':True},
            'scope':'Arbitrary interleaving of the original per-role transport/lifetime chains; all original scalar reads/writes and their cross-role dependencies discarded. Arbitrary common-frame linear resynthesis on existing live roles. No new frame path, storage, native correction price, global owner, precision or kappa claim.'}
    path=HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(result==json.loads(path.read_text()),'complete canonical receipt')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
