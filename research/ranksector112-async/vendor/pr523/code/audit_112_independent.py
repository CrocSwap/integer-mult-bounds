"""Independent raw-artifact audit of the 112-port restriction and whole owners.
Prepared for icekylinx with GPT-6 Astra assistance.

Does not import an emitter, hosting optimizer, nominated profile, nominated
windows, or the adapted PR514 checker.  Inputs are the original checked local
and global artifacts, the new literal local word/program, and 40,320 owners.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter, defaultdict
from functools import lru_cache
import argparse, gzip, hashlib, json, time

ap=argparse.ArgumentParser()
ap.add_argument('--original-base',type=Path,required=True)
ap.add_argument('--local',type=Path,required=True)
ap.add_argument('--owners',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args(); start_time=time.monotonic()

def read(p):
    data=p.read_bytes()
    return json.loads(gzip.decompress(data) if p.suffix=='.gz' else data)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(name,z):(a.out/name).write_text(json.dumps(z,indent=2,sort_keys=True)+'\n')
a.out.mkdir(parents=True,exist_ok=True)
old=read(a.original_base/'split-centres/CANONICAL-WORD.json.gz')
new=read(a.local/'CANONICAL-WORD.json.gz')
programs=read(a.local/'LOCAL-PROGRAMS.json.gz')
parent=read(a.original_base/'split-centres/GLOBAL-TEMPLATE.json.gz')
phase=read(a.original_base/'work/complex-nine-native/DATA-PHASES.json')
roles=read(a.owners)
V=new['v'];R=new['R'];N=2*V+R;H=new['h'];M=parent['m'];T=8
assert (old['v'],V,R,H,M)==(120,112,560,9,73)

# Infer the restriction from actual labels, not its producer's mapping file.
assert len(set(new['ports']))==V and set(new['ports'])<set(old['ports'])
kept=[i for i,q in enumerate(old['ports']) if q in set(new['ports'])]
assert [old['ports'][i] for i in kept]==new['ports']
rmp={oldi:newi for newi,oldi in enumerate(kept)}
rmp.update({120+oldi:V+newi for newi,oldi in enumerate(kept)})
rmp.update({240+h:2*V+h for h in range(R)})
removed=set(range(240+R))-set(rmp)
assert len(removed)==16 and new['frames']==old['frames']
removed_ops=Counter()
for name in ('A','B','precondition','compensation','cut','cleanup'):
    result=[]
    for event in old[name]:
        rs=event[1:3] if event[0]=='add' else event[1:2]
        if any(r in removed for r in rs):
            assert name=='cut' and event[0]=='add'
            assert event[1]==120+event[2] and event[3:5]==[1,1]
            removed_ops[name]+=1
            continue
        z=event.copy();z[1]=rmp[z[1]]
        if z[0]=='add':z[2]=rmp[z[2]]
        result.append(z)
    assert result==new[name],('not a literal restriction',name)
assert removed_ops=={'cut':8}
for name in ('start','final'):
    assert new[name]==[old[name][r] for r in sorted(rmp,key=rmp.get)]
assert new['centers']==[rmp[r] for r in old['centers'] if r in rmp]
assert new['center_frames']==[f for r,f in zip(old['centers'],old['center_frames']) if r in rmp]
assert new['target_levels']=={str(rmp[120+int(t)]-V):f for t,f in old.get('target_levels',{}).items()}
frames=new['frames']

@lru_cache(None)
def subspace(i):
    s={0}
    for x in frames[i]:s|={y^x for y in s}
    assert len(s)==1<<len(frames[i])
    return frozenset(s)

# Replay each literal local instruction, including all independent dirt columns.
# Recursive events contribute one child only after their actual endpoint frames
# have been checked. Scalar events are replayed as exact rational sparse rows.
local_results={}
for orientation,events in programs.items():
    state={('L',r):{r:Q(1)} for r in range(N)}
    cur={('L',r):new['start'][r] for r in range(N)}
    private=set(); profile=Counter(); current_phase=None; macros=0
    entries={r for r in range(2*V,N) if new['start'][r]!=0}
    adapters_seen=set();residual_seen=set();last_scalar=-1;first_post=None
    for event_index,event in enumerate(events):
        tag=event[0]
        if tag=='phase':current_phase=event[1];continue
        if tag=='climb':
            _,part,r,fr,to,rank=event
            assert current_phase==part and cur['L',r]==fr
            assert subspace(fr)<subspace(to) and rank==len(frames[to])-len(frames[fr])
            cur['L',r]=to;profile[rank]+=1
        elif tag=='center':
            _,k,fr,to,rank=event;reg=('C',k)
            assert current_phase=='centers' and reg in private and cur[reg]==fr
            assert subspace(fr)<subspace(to) or subspace(to)<subspace(fr)
            assert rank==abs(len(frames[to])-len(frames[fr]))
            cur[reg]=to;profile[rank]+=1
        elif tag=='adapter':
            _,kind,r,f=event
            assert (kind,r) not in adapters_seen;adapters_seen.add((kind,r))
            if kind=='old_to_new':
                assert current_phase=='entry_adapters' and r not in entries and f==new['start'][r]
            else:
                assert kind=='new_to_old' and current_phase=='exit_adapters' and f==new['final'][r]
        elif tag=='residual_adapter':
            _,kind,r,f=event
            assert r in entries and f==new['start'][r] and (kind,r) not in residual_seen
            residual_seen.add((kind,r))
            if kind=='pre':assert current_phase=='entry_adapters'
            else:
                assert kind=='post' and current_phase=='full_frame_cleanup'
                if first_post is None:first_post=event_index
        elif tag=='scalar':
            _,e,f=event;op=e[0];t=tuple(e[1]);macros+=1;last_scalar=event_index
            if op in ('clear','copy'):
                if op=='clear':
                    if t in private:assert cur[t]==f;private.remove(t)
                    state[t]={};cur[t]=f
                else:
                    source=tuple(e[2]);assert cur[source]==f
                    assert not state.get(t,{}) and t not in private
                    state[t]=state[source].copy();cur[t]=f;private.add(t)
            else:
                if t[0]=='C' and t not in private:
                    assert not state.get(t,{})
                    private.add(t);cur[t]=f
                assert cur[t]==f,(orientation,current_phase,'target-frame',t,cur[t],f)
                if op=='scale':
                    q=Q(e[2],e[3]);assert q
                    state[t]={j:q*x for j,x in state[t].items()}
                else:
                    assert op=='add';s=tuple(e[2]);assert t!=s and cur[s]==f
                    q=Q(e[3],e[4]);row=state[t]
                    for j,x in tuple(state[s].items()):
                        z=row.get(j,Q(0))+q*x
                        if z:row[j]=z
                        else:row.pop(j,None)
        else:raise AssertionError(('unknown local event',tag))
    assert not private and all(not row for reg,row in state.items() if reg[0]=='C')
    assert adapters_seen=={('old_to_new',r) for r in range(N) if r not in entries}|{('new_to_old',r) for r in range(N)}
    assert residual_seen=={(kind,r) for kind in ('pre','post') for r in entries}
    assert first_post is not None and first_post>last_scalar
    for r in range(N):
        desired={r:Q(1)}
        if orientation=='forward' and V<=r<2*V:desired[r-V]=Q(1)
        if orientation=='backward' and r<V:desired[V+r]=Q(-1)
        assert state['L',r]==desired,(orientation,r)
        assert cur['L',r]==new['final'][r]
    local_results[orientation]={'events':len(events),'scalar_macros':macros,'columns':N,'profile':dict(sorted(profile.items()))}
assert set(local_results)=={'forward','backward'}
local=Counter(local_results['forward']['profile'])
assert local==Counter(local_results['backward']['profile'])
assert local==Counter({int(r):n for r,n in new['local_profile'].items()})
widths=[H-len(frames[new['start'][2*V+h]]) for h in range(R)]
assert Counter(widths)=={7:18,8:154,9:388}
old_adapters=read(a.original_base/'split-centres/RESIDUAL-ADAPTERS.json')['recipes']
new_adapters=read(a.local/'RESIDUAL-ADAPTERS.json')['recipes']
for f in {new['start'][2*V+h] for h,w in enumerate(widths) if w<H}:
    assert new_adapters[str(f)]==old_adapters[str(f)]

# Derive the complete invocation order directly from its controller formula.
order=sorted(((s,rep) for s in range(9) for rep in range(T)),key=lambda z:(7*z[0]+6*z[1],z[0],z[1]))
pos_call={}; timeline=[]; blocks={};s=None
for event in parent['execution_schedule']:
    if event['kind'] in ('bank_padding_cover_sweep','translate_every_live_family'):continue
    if event['kind']=='local_cover_sweep':s=event['stage'];blocks[s]=[]
    assert s is not None;blocks[s].append(event)
for tm,(stage,rep) in enumerate(order):
    for e in blocks[stage]:
        if e['kind']=='local_cover_sweep':pos_call[stage,rep]=len(timeline)
        timeline.append((rep,e))
assert len(pos_call)==72
stage_pairs={e['stage']:e['pair'] for e in parent['recipe'] if e['kind']=='local'}
child_rank={}
for child in parent['idle_children']:
    i=child['child'];r=child['rank']
    assert i not in child_rank or child_rank[i]==r
    child_rank[i]=r
child_pair={};child_side={};windows={};last_touch={}
for pos,(rep,e) in enumerate(timeline):
    kind=e['kind']
    if kind=='local_cover_sweep':last_touch[rep,stage_pairs[e['stage']]]=pos
    elif kind=='bridge':
        last_touch[rep,e['src']]=pos;last_touch[rep,e['dst']]=pos
    elif kind=='idle_cover_sweep':
        pair=e['pair']
        for side,i in enumerate(e['child_indices']):
            if i in child_rank:
                child_pair[i]=pair;child_side[i]=side
                windows[rep,i]=(last_touch.get((rep,pair),-1),pos)
assert len(windows)==T*len(child_rank)

# Construct the actual orthogonal port charts by a transvection. Each chosen
# pending vector is checked as a vector, not merely a nominal offset.
phase_by_q={z['q']:z for z in phase['recipes']}
assert len(phase_by_q)==120
charts=[];idle_vectors={}
for port,q in enumerate(new['ports']):
    z=next(i for i in range(H) if not(q>>i)&1)
    a0=q^(1<<z);assert a0.bit_count()%2==0
    local_order=[z]+[i for i in range(H) if i!=z]
    # Only q needs to be first. Match the inherited chart's remaining order
    # by swapping z with 0, which is part of the fixed chart convention.
    local_order=list(range(H));local_order[0],local_order[z]=local_order[z],local_order[0]
    B=[(1<<i)^(a0 if (a0>>i)&1 else 0) for i in local_order]+[1<<i for i in range(H,M)]
    assert B[0]==q and len(set(B))==M
    assert all(((x&y).bit_count()&1)==int(i==j) for i,x in enumerate(B) for j,y in enumerate(B))
    charts.append(B)
    pr=phase_by_q[q]
    for i,rank in child_rank.items():
        axes=pr['idle_children'][i]['orthogonal_axes']
        assert len(axes)==rank==pr['idle_children'][i]['rank'] and all(x in B for x in axes)
        assert len(set(axes))==rank
        idle_vectors[port,i]=axes

# Every complete invocation contains all active data owners and exactly one
# assigned whole physical owner for every helper. Check full-family exclusion.
by_call=defaultdict(list);used=defaultdict(set);role_ids=set();family_roles=Counter();chart_hashes=set()
for role in roles:
    s,rep,h=role['stage'],role['replica'],role['helper']
    assert (s,rep,h) not in role_ids;role_ids.add((s,rep,h))
    assert 0<=h<R and role['time']==order.index((s,rep))
    fam=role['family'];orep,remainder=divmod(fam,8*V)
    pairside,port=divmod(remainder,V);pair,side=divmod(pairside,2)
    assert 0<=orep<T and role['owner_replica']==orep and role['port']==port
    assert role['copy']==orep*V+port
    i=role['child'];off=role['offset'];width=role['width']
    assert pair==child_pair[i] and side==child_side[i]
    assert width==widths[h] and 0<=off and off+width<=child_rank[i]
    lo,hi=windows[orep,i];assert lo<pos_call[s,rep]<hi
    occupied=set(range(off,off+width));key=(orep,i,port)
    assert not used[key]&occupied
    used[key]|=occupied;family_roles[fam]+=1;by_call[s,rep].append(fam)
    B=charts[port];actual=idle_vectors[port,i][off:off+width]
    assert len(actual)==width
    first=[B.index(x) for x in actual]
    spectators=[j for j in range(M) if j not in first][:H-width]
    orderB=first+spectators+[j for j in range(M) if j not in first+spectators]
    assert len(orderB)==len(set(orderB))==M and len(first+spectators)==H
    sigma=[B[j] for j in orderB]
    assert sigma[:width]==actual
    # All pairwise products inherit the already checked orthonormal basis.
    assert len(set(sigma))==M and set(sigma)==set(B)
    chart_hashes.add(hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest())
assert role_ids=={(s,rep,h) for s in range(9) for rep in range(T) for h in range(R)}
for (s,rep),helpers in by_call.items():
    active={rep*(8*V)+(2*stage_pairs[s]+side)*V+p for side in (0,1) for p in range(V)}
    assert len(active)==2*V and len(helpers)==R and len(set(helpers))==R
    assert not active&set(helpers)
    assert len(active|set(helpers))==N

# Recount every paid child from the literal local programs and the unused
# source idle axes. Never consume a nominated histogram or residual count.
paid=Counter({r:n*len(order) for r,n in local.items()});remainders=Counter();covered=0
for orep in range(T):
    for port in range(V):
        for i,rank in child_rank.items():
            cells=used[orep,i,port]
            assert cells==set(range(len(cells)))
            covered+=len(cells);left=rank-len(cells)
            assert left>=0
            if left:paid[left]+=1;remainders[left]+=1
stock=T*8*V;mass=sum(r*n for r,n in paid.items());deficit=M*stock-mass
assert covered==len(order)*sum(widths)
assert deficit==T*((9-1)*V-9*sum(len(frames[f]) for f in new['center_frames']))
assert M*M>2*max(paid)**2
result={
 'status':'PASS_INDEPENDENT_RAW_112_RESTRICTION_LOCAL_COLUMNS_CHARTS_WINDOWS_OWNERS_AND_PROFILE',
 'inputs':{str(p):digest(p) for p in [a.original_base/'split-centres/CANONICAL-WORD.json.gz',a.original_base/'split-centres/GLOBAL-TEMPLATE.json.gz',a.original_base/'work/complex-nine-native/DATA-PHASES.json',a.local/'CANONICAL-WORD.json.gz',a.local/'LOCAL-PROGRAMS.json.gz',a.local/'RESIDUAL-ADAPTERS.json',a.owners]},
 'local':local_results,'deleted_scalar_operations':dict(removed_ops),'deleted_canonical_ports':sorted(set(range(120))-set(kept)),
 'v':V,'helpers':R,'live':stock,'physical':stock+len(new['centers'])+R+2,
 'deficit':deficit,'rank_mass':mass,'paid_profile':dict(sorted(paid.items())),
 'residual_widths':dict(Counter(widths)),'whole_owner_roles':len(roles),'invocations':len(order),
 'all_owners_per_call_distinct':N,'pending_axes_covered':covered,'idle_remainders':dict(sorted(remainders.items())),
 'actual_orthogonal_charts':len(chart_hashes),'same_local_frames_and_residual_wrappers_as_PR514':True,
 'no_nominated_profile_or_windows_used':True,'no_emitter_or_hosting_checker_imported':True,
 'seconds':time.monotonic()-start_time,
 'scope':'Independent finite restriction, all rational scalar columns, nested local frames, fixed whole-owner schedule, actual port charts and paid histogram. The inherited all-size/compiler, common-label realization, precision/tape and analytic transfer interfaces remain conditions.'}
out('INDEPENDENT112-RAW-AUDIT.json',result)
print(json.dumps(result,indent=2))
