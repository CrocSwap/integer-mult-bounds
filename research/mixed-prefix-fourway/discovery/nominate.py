# Adapted from PR569 897213a855b7fb8a1b8b0e552a2f5c42e6c1b326; Apache-2.0.
# Changes: choose among four independently replayed PR571/572 providers; exact physical admission remains required.
#!/usr/bin/env python3
"""Nominate complete owner maps for the certified width-seven providers.

SciPy nominates only. Integral constraints and all expanded owners are checked
with integers; independent physical and arithmetic admission remains required.
"""
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import maximum_flow

WIDTHS = (4, 5, 7, 8, 9)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patterns(capacity, length, broad):
    if broad:
        result = []
        def visit(prefix, start, total):
            result.append(tuple(prefix))
            for i in range(start, len(WIDTHS)):
                w = WIDTHS[i]
                if total + w <= capacity and len(prefix) < length:
                    visit(prefix + [w], i, total + w)
        visit([], 0, 0)
        return result
    choices = {8: [(8,)],
               16: [(8, 8), (7, 9), (4, 9), (5, 9), (9,)],
               32: [(5, 9, 9, 9), (7, 8, 8, 9), (4, 9, 9, 9),
                    (5, 8, 9, 9), (5, 8, 8, 9), (5, 8, 8, 8), (8, 8, 8, 8)],
               48: [tuple([9] * n) for n in range(6)] + [(4, 8, 9, 9, 9, 9)]}
    return [p for p in choices[capacity] if len(p) <= length]


class Model:
    def __init__(self):
        self.upper, self.cost, self.rows, self.low, self.high = [], [], [], [], []
    def var(self, upper, cost=0):
        i = len(self.upper); self.upper.append(upper); self.cost.append(cost); return i
    def eq(self, row, low, high=None):
        self.rows.append(row); self.low.append(low); self.high.append(low if high is None else high)
    def solve(self, seconds):
        rr, cc, vv = [], [], []
        for i, row in enumerate(self.rows):
            for j, value in row.items():
                if value:
                    rr.append(i); cc.append(j); vv.append(value)
        matrix = coo_matrix((vv, (rr, cc)), shape=(len(self.rows), len(self.upper))).tocsc()
        result = milp(np.array(self.cost), integrality=np.ones(len(self.upper)),
                      bounds=Bounds(np.zeros(len(self.upper)), self.upper),
                      constraints=LinearConstraint(matrix, self.low, self.high),
                      options={'time_limit': seconds, 'mip_rel_gap': 0.0000001})
        print('MIP', len(self.upper), len(self.rows), result.status, result.message, flush=True)
        require(result.x is not None, 'No integer nomination')
        x = [int(round(v)) for v in result.x]
        require(max(abs(a-b) for a,b in zip(x,result.x)) < 1e-6, 'Nonintegral nomination')
        require(all(0 <= value <= self.upper[i] for i,value in enumerate(x)), 'Variable bound failed')
        for row, low, high in zip(self.rows, self.low, self.high):
            value = sum(coefficient*x[i] for i,coefficient in row.items())
            require(low <= value <= high, 'Exact integer constraint failed')
        return x, result


def expand_identical(pattern, copies, flows):
    """Regular bipartite multigraph decomposition gives one distinct-call bin per color."""
    from scipy.sparse.csgraph import maximum_bipartite_matching
    if not pattern:
        require(not flows,'Empty pattern flow');return [[]for _ in range(copies)]
    times=sorted({t for t,w in flows});slots=list(pattern);n=max(len(times),len(slots))
    require(len(times)>=len(slots),'Too few distinct calls for pattern')
    matrix=np.zeros((n,n),dtype=np.int64)
    for width in set(slots):
        right=[j for j,w in enumerate(slots)if w==width];j=0
        for ti,time in enumerate(times):
            count=flows.get((time,width),0)
            while count:
                require(j<len(right),'Excess width flow');r=right[j];take=min(count,copies-int(matrix[:,r].sum()))
                matrix[ti,r]+=take;count-=take
                if int(matrix[:,r].sum())==copies:j+=1
        require(all(int(matrix[:,r].sum())==copies for r in right),'Missing width flow')
    require(all(int(x)<=copies for x in matrix.sum(axis=1)),'Repeated call requires same owner')
    # Fill dummy right vertices to make the square multigraph copies-regular.
    j=len(slots)
    for ti in range(n):
        need=copies-int(matrix[ti].sum())
        while need:
            require(j<n,'Dummy completion overflow');take=min(need,copies-int(matrix[:,j].sum()))
            matrix[ti,j]+=take;need-=take
            if int(matrix[:,j].sum())==copies:j+=1
    require(all(int(x)==copies for x in matrix.sum(axis=0))and all(int(x)==copies for x in matrix.sum(axis=1)),'Nonregular completion')
    result=[]
    for color in range(copies):
        match=maximum_bipartite_matching(csr_matrix(matrix>0),perm_type='column')
        require(len(match)==n and set(map(int,match))==set(range(n)),'Missing perfect matching')
        owner=[]
        for ti,r in enumerate(match):
            require(matrix[ti,r]>0,'Matching absent edge');matrix[ti,r]-=1
            if r<len(slots):owner.append((times[ti],slots[r]))
        require(Counter(w for t,w in owner)==Counter(pattern)and len({t for t,w in owner})==len(owner),'Bad matched owner')
        result.append(owner)
    require(not matrix.any(),'Unconsumed multigraph edge')
    require(Counter((t,w)for owner in result for t,w in owner)==Counter(flows),'Expanded flow mismatch')
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--plain-local',type=Path,required=True)
    ap.add_argument('--width7-local',type=Path,required=True)
    ap.add_argument('--four-local',type=Path,required=True)
    ap.add_argument('--prefix-local',type=Path,required=True)
    ap.add_argument('--fixed-patterns',type=Path)
    ap.add_argument('--fixed-counts',type=str)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seconds',type=float,default=120)
    ap.add_argument('--broad',action='store_true')
    ap.add_argument('--selected',type=int)
    args=ap.parse_args()
    require(not args.out.exists(),'Use a fresh output directory')
    source_plan=args.source/'data/PLAN.json'; source_owners=args.source/'data/OWNERS.json.gz'
    plan=read(source_plan)
    registry={}
    template=plan['provider_registry']['rank5_eight_cold']
    for pid,directory in [('plain_four',args.four_local),('plain_eight',args.plain_local),('width7_eight',args.width7_local),('prefix_width7_eight',args.prefix_local)]:
        canonical=read(directory/'CANONICAL-WORD.json.gz');checks=read(directory/'LOCAL-CHECKS.json')
        d=copy.deepcopy(template)
        d['widths']=[9-len(canonical['frames'][frame]) for frame in canonical['start'][224:]]
        d['artifact_sha256']={name:sha(directory/name) for name in d['artifact_sha256']}
        d['actual_paid_profile']=checks['forward']['paid_profile']
        require(checks['forward']['paid_profile']==checks['backward']['paid_profile'],'Unequal orientation profiles')
        d['orientation_program_sha256']={k:v['sha256'] for k,v in checks.items()}
        registry[pid]=d
    inventories={pid:Counter(d['widths']) for pid,d in registry.items()}
    require(inventories=={'plain_four':Counter({4:8,5:48,8:160,9:288}),
       'plain_eight':Counter({4:8,5:48,8:164,9:284}),
       'width7_eight':Counter({4:8,5:48,7:32,8:132,9:284}),
       'prefix_width7_eight':Counter({4:8,5:48,7:32,8:128,9:288})},'Wrong provider inventories')
    entropy=lambda profile:sum(int(k)*v*math.log(int(k)) for k,v in profile.items())
    baseline_entropy=entropy(registry['plain_four']['actual_paid_profile'])
    model=Model(); selections={(t,p):model.var(1,baseline_entropy-entropy(registry[p]['actual_paid_profile']))for t in range(72)for p in registry}
    for time in range(72):model.eq({selections[time,p]:1 for p in registry},1)
    if args.fixed_counts:
        counts=json.loads(args.fixed_counts)
        for p,n in counts.items():model.eq({selections[t,p]:1 for t in range(72)},n)
    frozen_patterns=None
    if args.fixed_patterns:
        frozen_patterns=read(args.fixed_patterns)['allocations']
        frozen_patterns={(v['replica'],v['child']):v['patterns'] for v in frozen_patterns}
    groups=[]; totalflow=defaultdict(dict)
    for key,(capacity,window) in plan['windows'].items():
        replica,child=map(int,key.split(',')); choices=patterns(capacity,len(window),args.broad)
        counts=[Counter(p) for p in choices]
        pv=[model.var(112,-(capacity-sum(p))*math.log(capacity-sum(p)) if capacity-sum(p)>1 else 0) for p in choices]
        model.eq({i:1 for i in pv},112)
        if frozen_patterns is not None:
            frozen=frozen_patterns[replica,child]
            require(set(frozen)<=set(map(str,choices)),'Pattern absent from model')
            for p,i in zip(choices,pv):model.eq({i:1},frozen.get(str(p),0))
        flows={}
        for pi,count in enumerate(counts):
            for time in window:
                row={pv[pi]:-1}
                for width,n in count.items():
                    i=model.var(112);flows[pi,time,width]=i;totalflow[time,width][i]=1;row[i]=1
                if count:model.eq(row,-np.inf,0)
            for width,n in count.items():
                row={i:1 for (p,t,w),i in flows.items()if p==pi and w==width};row[pv[pi]]=-n
                model.eq(row,0)
        groups.append(dict(replica=replica,child=child,capacity=capacity,window=window,patterns=choices,pv=pv,flows=flows))
    for time in range(72):
        for width in WIDTHS:
            row=dict(totalflow[time,width])
            for p in registry:row[selections[time,p]]=-inventories[p][width]
            model.eq(row,0)
    print('EXACT PATTERN MODEL',len(model.upper),len(model.rows),flush=True)
    x,opt=model.solve(args.seconds)
    selected={time:p for (time,p),i in selections.items()if x[i]}
    require(len(selected)==72,'Incomplete provider selection')
    print('Selected',selected,flush=True)
    args.out.mkdir(parents=True)
    (args.out/'WINDOW-SOLUTION.json').write_text(json.dumps(dict(selected=selected,x=x,variables=len(model.upper),constraints=len(model.rows)))+'\n')
    plan['provider_registry']=registry
    source_calls=plan['provider_calls']
    plan['provider_calls']=[];plan['per_call_widths']=[]
    pools=defaultdict(list);paid=Counter()
    for time,(stage,replica) in enumerate(plan['order']):
        pid=selected[time];d=registry[pid]
        # Preserve the source's exact orientation contract rather than inferring
        # it from an arbitrary half of the nine complete-call stages.
        original=source_calls[time]
        orientation=original['orientation']
        plan['provider_calls'].append(dict(time=time,stage=stage,replica=replica,provider=pid,orientation=orientation,local_program_sha256=d['orientation_program_sha256'][orientation]))
        plan['per_call_widths'].append(dict(stage=stage,replica=replica,widths=d['widths']))
        paid.update({int(k):v for k,v in d['actual_paid_profile'].items()})
        for helper,width in enumerate(d['widths']):pools[time,width].append(helper)
    rebuilt=[];allocations=[]
    for gi,g in enumerate(groups):
        plist=[];slots=[];flows=Counter()
        for pi,(pattern,var) in enumerate(zip(g['patterns'],g['pv'])):
            count=x[var]
            per_pattern={(time,width):x[i]for (j,time,width),i in g['flows'].items()if j==pi and x[i]}
            flows.update(per_pattern)
            if count:
                plist.extend([pattern]*count)
                slots.extend(expand_identical(pattern,count,per_pattern))
            else:require(not per_pattern,'Flow through zero pattern count')
        require(len(slots)==112,'Wrong port count')
        require(Counter((t,w) for s in slots for t,w in s)==Counter(flows),'Wrong expanded flow')
        for port,s in enumerate(slots):
            require(Counter(w for _,w in s)==Counter(plist[port]),'Wrong expanded pattern')
            require(len({t for t,_ in s})==len(s),'Repeated owner in expanded call')
            offset=0
            for time,width in sorted(s):
                require(pools[time,width],'Missing helper');helper=pools[time,width].pop()
                stage,replica=plan['order'][time];r,c=g['replica'],g['child']
                rebuilt.append(dict(child=c,copy=r*112+port,family=r*896+(2*plan['pairs'][str(c)]+plan['sides'][str(c)])*112+port,helper=helper,offset=offset,owner_replica=r,port=port,replica=replica,stage=stage,time=time,width=width))
                offset+=width
        allocations.append(dict(replica=g['replica'],child=g['child'],capacity=g['capacity'],patterns=dict(Counter(str(p) for p in plist))))
        if gi%16==0:print('Expanded',gi,'/',len(groups),flush=True)
    require(not any(pools.values()),'Unassigned helper')
    occupied=defaultdict(set);families=defaultdict(set);helpers=defaultdict(set)
    for row in rebuilt:
        t,f,h=row['time'],row['family'],row['helper']
        require(f not in families[t] and h not in helpers[t],'Repeated complete-call owner/helper')
        families[t].add(f);helpers[t].add(h)
        cap,window=plan['windows'][f"{row['owner_replica']},{row['child']}"]
        require(t in window and 0<=row['offset'] and row['offset']+row['width']<=cap,'Invalid owner window/footprint')
        key=row['owner_replica'],row['child'],row['port'];cells=set(range(row['offset'],row['offset']+row['width']))
        require(not occupied[key]&cells,'Overlapping owner cells');occupied[key]|=cells
        call=plan['provider_calls'][t]
        require(row['width']==registry[call['provider']]['widths'][h],'Wrong literal helper width')
    require(all(helpers[t]==set(range(504)) for t in range(72)),'Incomplete calls')
    remainders=Counter()
    for key,(cap,_) in plan['windows'].items():
        r,c=map(int,key.split(','))
        for port in range(112):
            cells=occupied[r,c,port];require(cells==set(range(len(cells))),'Nonprefix owner')
            if len(cells)<cap:remainders[cap-len(cells)]+=1
    paid.update(remainders);require(sum(k*v for k,v in paid.items())==520704,'Changed total rank mass')
    rebuilt.sort(key=lambda r:(r['time'],r['helper']))
    packed=gzip.compress(json.dumps(rebuilt,sort_keys=True,separators=(',',':')).encode(),mtime=0)
    packed=packed[:9]+b'\xff'+packed[10:]
    (args.out/'OWNERS.json.gz').write_bytes(packed)
    plan.update(status='WIDTH7_LITERAL_OWNER_NOMINATION_PENDING_ADMISSION',profile=dict(sorted(paid.items())),source_plan_sha256=sha(source_plan),source_owners_sha256=sha(source_owners),assignment_sha256=sha(args.out/'OWNERS.json.gz'))
    (args.out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
    receipt=dict(status='PASS_EXACT_LITERAL_OWNER_NOMINATION_PENDING_PHYSICAL_ADMISSION',source_plan_sha256=sha(source_plan),source_owners_sha256=sha(source_owners),owners_sha256=sha(args.out/'OWNERS.json.gz'),plan_sha256=sha(args.out/'PLAN.json'),selected_provider_by_time=selected,provider_counts=dict(Counter(selected.values())),profile=dict(sorted(paid.items())),idle_remainders=dict(sorted(remainders.items())),allocations=allocations,scope='Solver nomination only; all integral constraints, literal helper widths, complete calls, whole-owner windows, disjoint prefixes and total rank checked. Independent physical and exact arithmetic admission remain required.')
    (args.out/'NOMINATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('provider_counts','profile','idle_remainders')}),flush=True)

if __name__=='__main__':main()
