"""Deterministic deadline placement of compensated reads and late scratch reuse.

The local scalar DAG, operation frames and source gauges stay fixed. Every
read is placed before its role's first workspace gate and before larger
frames on any reached target. A donor must finish before the recipient's
read. All aliases remain disjoint pairs. Prepared with OpenAI Codex assistance.
"""
from collections import defaultdict
from functools import lru_cache
from reuse import basis,complement


def select(data):
    ops=data['ops'];sigma={s:basis(F)for s,F in data['placed'].items()};frames=data['op_frames']
    h,v,R=data['h'],data['v'],data['R'];old=[dict(p)for p in data['reuse_pairs']]
    used={x for p in old for x in (p['donor'],p['recipient'])}
    order=[i for i in data['phase1']+data['rest']if ops[i][0]!='src'];positions={i:j for j,i in enumerate(order)}
    assert all(ops[i][0]!='src'for i in data['phase1']);cut=len(data['phase1'])
    first={};last={}
    for i in order:
        for s in ops[i][1:3]:first.setdefault(s,i);last[s]=i
    assert last==data['last']
    levels=defaultdict(list)
    for s,F in sigma.items():levels[len(F)].append(s)
    limit=[len(order)]*v;deadline={}
    for d,roles in sorted(levels.items(),reverse=True):
        for s in sorted(roles):
            birth=cut if s in data['leaf_of']else positions[first[s]]
            deadline[s]=min([birth]+[limit[t]for t in data['reach'][s]])
            assert deadline[s]>=cut
        # Equal frames need not order each other. Their minimum deadline
        # constrains only subsequent strictly smaller target-frame levels.
        for s in roles:
            for t in data['reach'][s]:limit[t]=min(limit[t],deadline[s])
    recipients=[s for s in sorted(sigma)if s not in used and s not in data['leaf_of']and s not in data['touched']and deadline[s]>cut]
    donors=[s for s in sorted(last)if s not in used and s not in sigma and s not in data['role_root']]
    groups=defaultdict(list)
    for s in donors:groups[frames[last[s]]].append(s)
    perps={sigma[s]:complement(sigma[s],h)for s in recipients}
    @lru_cache(None)
    def fits(A,B):return all(not((a&n).bit_count()&1)for a in A for n in perps[B])
    edges={}
    for b in recipients:
        assert ops[first[b]][0]=='copy'and ops[first[b]][2]==b
        pool=[]
        for A,roles in sorted(groups.items()):
            if len(A)<=len(sigma[b])and fits(A,sigma[b]):
                pool.extend(s for s in roles if positions[last[s]]<deadline[b])
        if pool:edges[b]=sorted(pool,key=lambda a:(-len(frames[last[a]]),positions[last[a]],a))
    match={}
    def augment(b,seen):
        for a in edges.get(b,()):
            if a in seen:continue
            seen.add(a)
            if a not in match or augment(match[a],seen):match[a]=b;return True
        return False
    for b in sorted(edges,key=lambda b:(len(edges[b]),positions[first[b]],b)):augment(b,set())
    added=[]
    for a,b in sorted(match.items()):
        A=frames[last[a]];F=sigma[b]
        added.append(dict(donor=a,recipient=b,donor_frame=A,birth_frame=F,e=len(A),s=len(F)))
    paired=old+added
    stats=dict(new_pairs=len(added),previous_pairs=len(old),all_pairs=len(paired),
      physical_roles_before=R-len(old),physical_roles_after=R-len(paired),
      candidate_donors=len(donors),candidate_recipients=len(recipients),
      delayed_read_roles=sum(t>cut for t in deadline.values()),
      changed_gates=0,changed_source_gauges=0,matching_order='Recipient degree then first gate then role; donors by descending last-frame dimension, death, then role',
      phase_one_cut=cut,scalar_dag_unchanged=True,operation_frames_unchanged=True,
      source_gauges_unchanged=True,target_histograms_unchanged=True)
    return paired,dict(sorted(deadline.items())),sorted(p['recipient']for p in added),stats
