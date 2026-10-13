"""Exact callwise concave-cost owner matching over every legal idle family.

This is a finite integer nomination algorithm, not a MILP. Each greedy
matching is optimal for every concave remainder cost. Its majorization
receipt is checked with integers, independently of floating root screens.
"""
from collections import Counter, defaultdict, deque
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import time

from reuse_owners import read, packed, sha, signature, audit_roles, rate


def stoploss(hist,k):return sum(n*max(r-k,0) for r,n in hist.items())


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--owners',type=Path,required=True)
    ap.add_argument('--signature',action='append',required=True,help='Existing PID=verified native directory or raw/signature JSON')
    ap.add_argument('--max-passes',type=int,default=8)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();assert 1<=a.max_passes<=12
    a.out.mkdir(parents=True,exist_ok=False);beg=time.monotonic()
    plan,oldroles=read(a.plan),read(a.owners);V,M=112,73
    assert (plan['K'],plan['T'],plan['M'],plan['L'])==(4,8,73,9)
    sig={pid:{'widths':desc['widths'],'profile':{int(r):n for r,n in desc['actual_paid_profile'].items()},'source':'input PLAN'} for pid,desc in plan['provider_registry'].items()}
    for spec in a.signature:
        pid,path=spec.split('=',1);assert pid in sig;sig[pid]=signature(path)
    R=len(next(iter(sig.values()))['widths'])
    for s in sig.values():
        assert len(s['widths'])==R and all(type(w) is int and 0<w<=9 for w in s['widths'])
        assert sum(r*n for r,n in s['profile'].items())==16*V+64+sum(s['widths'])
    calls={(c['stage'],c['replica']):c for c in plan['provider_calls']}
    order=[tuple(c) for c in plan['order']]
    oldwidths={k:plan['provider_registry'][c['provider']]['widths'] for k,c in calls.items()}
    widths={k:sig[c['provider']]['widths'] for k,c in calls.items()}
    audit_roles(oldroles,plan,oldwidths,V,R)
    caps={};families={};eligible=defaultdict(list)
    for key,(cap,window) in plan['windows'].items():
        rep,ch=map(int,key.split(','))
        for port in range(V):
            g=(rep,ch,port);caps[g]=cap
            families[g]=rep*(8*V)+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*V+port
            for t in window:eligible[t].append(g)
    for t,gs in eligible.items():
        assert len({families[g] for g in gs})==len(gs), 'current geometry requires one eligible child per family'
        s,rep=order[t];active_pair=max(0,(s-1)//2)
        assert all(not (g[0]==rep and plan['pairs'][str(g[1])]==active_pair) for g in gs), 'active data family in idle window'
    current=defaultdict(dict);used={g:0 for g in caps}
    for z in oldroles:
        c=(z['stage'],z['replica']);g=(z['owner_replica'],z['child'],z['port'])
        current[c][z['helper']]=(g,z['width']);used[g]+=z['width']
    assert all(0<=used[g]<=caps[g] for g in caps)
    moves=[]

    def idle_profile():return Counter(caps[g]-used[g] for g in caps if caps[g]>used[g])

    def total_profile():
        p=Counter()
        for c in plan['provider_calls']:p.update(sig[c['provider']]['profile'])
        p.update(idle_profile());assert M*plan['live']-sum(r*n for r,n in p.items())==2560
        return p

    def update(call,bootstrap=False):
        t=calls[call]['time'];gs=eligible[t]
        old=current[call]
        old_by_group={g:(h,w) for h,(g,w) in old.items()}
        assert len(old_by_group)==R and set(old_by_group)<=set(gs)
        oldhist=Counter(caps[g]-used[g] for g in gs)
        for g,(h,w) in old_by_group.items():used[g]-=w
        want=defaultdict(set)
        for h,w in enumerate(widths[call]):want[w].add(h)
        # Equal-capacity opportunities have identical costs. Preserve old
        # matching widths first, then old owners, and finally family order.
        buckets=defaultdict(lambda:defaultdict(deque))
        for g in sorted(gs,key=lambda g:(families[g],g[1])):
            available=caps[g]-used[g];oldw=old_by_group.get(g,(None,0))[1]
            buckets[available][oldw].append(g)
        result={};unassigned=R
        for c in sorted(buckets):
            bucket=buckets[c]
            while unassigned and any(bucket.values()):
                w=next((w for w in sorted(want,reverse=True) if w<=c and want[w]),None)
                if w is None:break
                if bucket.get(w):q=w
                else:q=next(q for q in sorted(bucket,reverse=True) if bucket[q])
                g=bucket[q].popleft()
                h0=old_by_group.get(g,(None,0))[0]
                h=h0 if h0 in want[w] else min(want[w])
                want[w].remove(h);result[h]=(g,w);used[g]+=w;unassigned-=1
                assert used[g]<=caps[g]
        assert unassigned==0,('no legal family matching',call,{w:len(h) for w,h in want.items() if h})
        assert set(result)==set(range(R)) and len({families[g] for g,w in result.values()})==R
        newhist=Counter(caps[g]-used[g] for g in gs)
        equal_widths=Counter(w for g,w in old.values())==Counter(widths[call])
        strict=False
        if equal_widths:
            assert sum(oldhist.values())==sum(newhist.values())
            assert stoploss(oldhist,0)==stoploss(newhist,0)
            margins=[stoploss(newhist,k)-stoploss(oldhist,k) for k in range(49)]
            assert min(margins)>=0,('greedy did not majorize old assignment',call,margins)
            strict=any(margins)
        else:
            assert bootstrap
            margins=None
        changed=sum(result[h]!=old[h] for h in result)
        current[call]=result
        moves.append({'stage':call[0],'replica':call[1],'time':t,'bootstrap':bootstrap,
                      'equal_width_multiset':equal_widths,'integer_stoploss_margins':margins,
                      'strict_majorization':strict,'changed_helper_owners':changed})
        return strict,changed

    changed_calls=[c for c in order if any(current[c][h][1]!=widths[c][h] for h in range(R))]
    for c in changed_calls:update(c,bootstrap=True)
    p=total_profile();baseline_b=rate(p,2560,M)
    rounds=[{'pass':'bootstrap','changed_provider_calls':[list(c) for c in changed_calls],
             'floating_b':baseline_b,'remainder_profile':dict(sorted(idle_profile().items()))}]
    print(json.dumps({'checkpoint':'all_goal_signatures_feasible','bootstrap_calls':len(changed_calls),'floating_b':baseline_b}),flush=True)
    quiet=0
    for passno in range(a.max_passes):
        strict=changed=0
        for c in (order if passno%2==0 else list(reversed(order))):
            s,z=update(c);strict+=bool(s);changed+=z
        p=total_profile();r={'pass':passno+1,'strictly_improved_calls':strict,'changed_helper_owners':changed,
                             'floating_b':rate(p,2560,M),'remainder_profile':dict(sorted(idle_profile().items()))}
        rounds.append(r);print(json.dumps({k:r[k] for k in ('pass','strictly_improved_calls','changed_helper_owners','floating_b')}),flush=True)
        quiet=quiet+1 if not strict else 0
        if quiet>=2 or (not strict and not changed):break

    groups=defaultdict(list);roles=[]
    for call in order:
        s,rep=call;t=calls[call]['time']
        for h,(g,w) in current[call].items():
            orp,ch,port=g
            z={'child':ch,'copy':orp*V+port,'family':families[g],'helper':h,'offset':0,
               'owner_replica':orp,'port':port,'replica':rep,'stage':s,'time':t,'width':w}
            roles.append(z);groups[g].append(z)
    for g,zs in groups.items():
        off=0
        for z in sorted(zs,key=lambda z:(z['time'],z['helper'])):z['offset']=off;off+=z['width']
        assert off==used[g]<=caps[g]
    roles.sort(key=lambda z:(z['time'],z['helper']))
    cells,_=audit_roles(roles,plan,widths,V,R)
    for z in roles:
        active=max(0,(z['stage']-1)//2)
        assert not (z['owner_replica']==z['replica'] and plan['pairs'][str(z['child'])]==active)
    for g in caps:assert len(cells[g])==used[g]
    remainder=[]
    for g in caps:
        left=caps[g]-used[g]
        if left:
            rep,ch,port=g
            remainder.append({'child':ch,'port':port,'replica':rep,'replicas':1,'family':families[g],
                              'rank':left,'hosted':used[g],'pending_offset':used[g]})
    profile=dict(sorted(total_profile().items()));assert M*M>2*max(profile)**2
    raw=packed(roles);compressed=bytearray(gzip.compress(raw,mtime=0));compressed[9]=255
    (a.out/'OWNERS.json.gz').write_bytes(bytes(compressed))
    (a.out/'MAJORIZATION.json.gz').write_bytes(gzip.compress(packed(moves),mtime=0))
    (a.out/'REMAINDERS.json').write_text(json.dumps(remainder,indent=2)+'\n')
    (a.out/'PROFILE.json').write_text(json.dumps(profile,indent=2)+'\n')
    fields={'profile':profile,'per_call_widths':[{'stage':s,'replica':r,'widths':widths[s,r]} for s,r in order],
            'assignment_sha256':hashlib.sha256(raw).hexdigest(),'assignment_sha256_semantics':'SHA256 sorted-key compact uncompressed OWNERS array',
            'source_owners_sha256':sha(a.owners),'provider_signatures':sig}
    (a.out/'PLAN-OWNER-FIELDS.json').write_text(json.dumps(fields,indent=2)+'\n')
    receipt={'status':'PASS_EXPANDED_OWNER_MATCHING_EXACT_COMBINATORICS_PENDING_GLOBAL_ADMISSION',
             'source_plan':str(a.plan),'source_plan_sha256':sha(a.plan),'source_owners':str(a.owners),'source_owners_sha256':sha(a.owners),
             'owners_sha256':sha(a.out/'OWNERS.json.gz'),'source_signatures':sig,
             'roles':len(roles),'calls':len(order),'unchanged_call_order_and_windows':True,
             'all_families_idle_and_outside_active_data':True,'one_helper_per_family_per_call':True,
             'all_footprints_disjoint_compacted_prefixes':True,'integer_majorization_steps':sum(z['equal_width_multiset'] for z in moves),
             'majorization_sha256':sha(a.out/'MAJORIZATION.json.gz'),'matching_rounds':rounds,
             'global_profile':profile,'rank_mass':sum(r*n for r,n in profile.items()),'deficit':2560,
             'remainder_profile':dict(sorted(idle_profile().items())),'maxchild':max(profile),
             'candidate_floating_screen_b':rate(profile,2560,M),'seconds':time.monotonic()-beg,
             'remaining_admission':'Fresh native-provider bindings, actual 73-column owner charts, independent full controller audit, finite invoice, exact moment and outer assembly.'}
    (a.out/'EXPANDED-OWNER-REUSE.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','roles','remainder_profile','rank_mass','candidate_floating_screen_b','seconds')},indent=2),flush=True)


if __name__=='__main__':main()
