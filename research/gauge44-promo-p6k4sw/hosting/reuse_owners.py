"""Deterministic existing-family owner reuse and optional callwise matching.

The output is a nomination, requiring the ordinary independent owner, phase,
finite-invoice, and exact-moment admission. No MILP or new owner family is used.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import json
import math
import time


def read(path):
    raw=Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def packed(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def signature(path):
    path=Path(path)
    if path.is_dir():
        w=read(path/'CANONICAL-WORD.json.gz');V,R=w['v'],w['R']
        widths=[len(w['frames'][w['final'][2*V+h]])-len(w['frames'][w['start'][2*V+h]]) for h in range(R)]
        programs=read(path/'LOCAL-PROGRAMS.json.gz')
        profiles=[Counter(e[-1] for e in programs[o] if e[0] in ('climb','center')) for o in ('forward','backward')]
        assert profiles[0]==profiles[1]
        assert profiles[0]=={int(r):n for r,n in w['local_profile'].items()}
        return {'widths':widths,'profile':dict(profiles[0]),'source':str(path),
                'canonical_sha256':sha(path/'CANONICAL-WORD.json.gz'),
                'program_sha256':sha(path/'LOCAL-PROGRAMS.json.gz')}
    w=read(path)
    if 'report' in w:
        V,R=w['report']['v'],w['report']['R']
        widths=[len(w.get('helper_final',{}).get(str(2*V+h),range(9)))-len(w.get('start_extra',{}).get(str(2*V+h),[])) for h in range(R)]
        profile={int(r):n for r,n in w['report']['local_profile'].items()}
    else:
        widths=w['widths'];profile={int(r):n for r,n in w['profile'].items()}
    return {'widths':widths,'profile':profile,'source':str(path),'source_sha256':sha(path)}


def phi(rank,b,M):return rank*math.expm1(b*math.log(M/rank)) if rank else 0.


def rate(profile,deficit,M):
    lo,hi=0.,.02
    for _ in range(58):
        mid=(lo+hi)/2
        if sum(n*phi(r,mid,M) for r,n in profile.items())<deficit:lo=mid
        else:hi=mid
    return lo


def audit_roles(roles,plan,widths_by_call,V,R):
    used=defaultdict(set);families=defaultdict(set);helpers=defaultdict(set)
    for z in roles:
        s,rep,h=z['stage'],z['replica'],z['helper'];call=(s,rep)
        assert z['time']==plan['order'].index([s,rep])
        assert 0<=h<R and z['width']==widths_by_call[call][h]
        assert h not in helpers[call] and z['family'] not in families[call]
        helpers[call].add(h);families[call].add(z['family'])
        orp,ch,port=z['owner_replica'],z['child'],z['port']
        assert z['copy']==orp*V+port
        assert z['family']==orp*(8*V)+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*V+port
        cap,window=plan['windows'][f'{orp},{ch}']
        assert z['time'] in window and 0<=z['offset'] and z['offset']+z['width']<=cap
        cells=set(range(z['offset'],z['offset']+z['width']))
        key=(orp,ch,port);assert not used[key]&cells;used[key]|=cells
    assert len(roles)==len(plan['order'])*R
    assert all(helpers[tuple(c)]==set(range(R)) for c in plan['order'])
    for cells in used.values():assert cells==set(range(len(cells)))
    return used,families


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--owners',type=Path,required=True)
    ap.add_argument('--signature',action='append',default=[],help='Existing PID=raw-word, signature JSON, or verified native directory')
    ap.add_argument('--passes',type=int,default=2)
    ap.add_argument('--price-b',type=float,default=0.001638923)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();assert 0<=a.passes<=2
    a.out.mkdir(parents=True,exist_ok=False);beg=time.monotonic()
    plan,oldroles=read(a.plan),read(a.owners)
    assert (plan['K'],plan['T'],plan['M'],plan['L'])==(4,8,73,9)
    M,V=73,112;R=len(next(iter(plan['provider_registry'].values()))['widths'])
    signatures={pid:{'widths':desc['widths'],'profile':{int(r):n for r,n in desc['actual_paid_profile'].items()},'source':'inherited PLAN'} for pid,desc in plan['provider_registry'].items()}
    for spec in a.signature:
        pid,path=spec.split('=',1);assert pid in signatures
        signatures[pid]=signature(path)
    for sig in signatures.values():
        assert len(sig['widths'])==R and all(type(w) is int and 0<w<=9 for w in sig['widths'])
        assert sum(int(r)*n for r,n in sig['profile'].items())==16*V+64+sum(sig['widths'])
    calls={(c['stage'],c['replica']):c for c in plan['provider_calls']}
    oldwidths={k:plan['provider_registry'][c['provider']]['widths'] for k,c in calls.items()}
    newwidths={k:signatures[c['provider']]['widths'] for k,c in calls.items()}
    oldused,oldfamilies=audit_roles(oldroles,plan,oldwidths,V,R)

    # A slot is an old immutable owner-family opportunity. Only the helper
    # assigned to the opportunity and its footprint width may change.
    bycall=defaultdict(list);groups=defaultdict(list)
    for i,z in enumerate(oldroles):
        bycall[z['stage'],z['replica']].append(i)
        groups[z['owner_replica'],z['child'],z['port']].append(i)
    group_of={i:g for g,ids in groups.items() for i in ids}
    cap={g:plan['windows'][f'{g[0]},{g[1]}'][0] for g in groups}
    assigned_h={};assigned_w={};dominance={};pending=[]
    for call,ids in bycall.items():
        slots=sorted(ids,key=lambda i:(oldroles[i]['width'],oldroles[i]['helper']))
        helpers=sorted(range(R),key=lambda h:(newwidths[call][h],h))
        failures=[(h,newwidths[call][h],oldroles[i]['width']) for h,i in zip(helpers,slots) if newwidths[call][h]>oldroles[i]['width']]
        if failures:
            # Keep this call's old widths provisionally; shrunk calls leave
            # slack on their original owner families. A subsequent exact
            # bipartite matching may use that slack for this call.
            pending.append(call)
            for i in ids:assigned_h[i]=oldroles[i]['helper'];assigned_w[i]=oldroles[i]['width']
        else:
            for h,i in zip(helpers,slots):assigned_h[i]=h;assigned_w[i]=newwidths[call][h]
        dominance[str(call)]={'old_total':sum(oldwidths[call]),'new_total':sum(newwidths[call]),'sorted_termwise_dominance':not failures,'failed_positions':failures}
    used={g:sum(assigned_w[i] for i in ids) for g,ids in groups.items()}
    assert all(used[g]<=cap[g] for g in groups)
    cost_cache=[phi(r,a.price_b,M) for r in range(49)]
    def current_cost():return sum(cost_cache[cap[g]-used[g]] for g in groups)
    passes=[{'pass':'sorted','touched_group_idle_pressure':current_cost(),'calls_awaiting_capacity_matching':len(pending)}]

    if a.passes or pending:
        import numpy as np
        from scipy.optimize import linear_sum_assignment
        def match_call(call,force=False):
            ids=sorted(bycall[call],key=lambda i:oldroles[i]['helper'])
            gs=[group_of[i] for i in ids]
            assert len(set(gs))==R, 'one owner family per complete call is essential'
            available=np.array([cap[g]-used[g]+assigned_w[i] for i,g in zip(ids,gs)],dtype=np.int64)
            ws=np.array(newwidths[call],dtype=np.int64)
            left=available[None,:]-ws[:,None]
            matrix=np.full((R,R),np.inf)
            valid=left>=0
            matrix[valid]=np.asarray(cost_cache)[left[valid]]
            ri,ci=linear_sum_assignment(matrix)
            assert len(ri)==R and np.all(np.isfinite(matrix[ri,ci]))
            oldcost=sum(cost_cache[cap[g]-used[g]] for g in gs)
            newcost=float(matrix[ri,ci].sum())
            if not force:
                assert newcost<=oldcost+1e-10
                if oldcost-newcost<=1e-10:return False
            for h,col in zip(ri,ci):
                i=ids[int(col)];g=group_of[i];h=int(h);ww=int(ws[h])
                used[g]+=ww-assigned_w[i];assigned_w[i]=ww;assigned_h[i]=h
                assert used[g]<=cap[g]
            return True
        for call in pending:
            match_call(call,force=True)
            dominance[str(call)]['capacity_matching_feasible']=True
        if pending:passes.append({'pass':'capacity_bootstrap','touched_group_idle_pressure':current_cost(),'resolved_calls':[list(c) for c in pending]})
        for p in range(a.passes):
            accepted=0;startcost=current_cost()
            order=[tuple(k) for k in plan['order']]
            if p%2:order.reverse()
            for call in order:
                accepted+=match_call(call)
            finalcost=current_cost();assert finalcost<=startcost+1e-9
            passes.append({'pass':p+1,'accepted_calls':accepted,'touched_group_idle_pressure':finalcost,'decrease':startcost-finalcost})

    # The inherited compiler requires each used coordinate set to be a
    # prefix. Stable left compaction preserves every immutable owner field.
    roles=copy.deepcopy(oldroles);matching=[]
    for g,ids in groups.items():
        off=0
        for i in sorted(ids,key=lambda i:(oldroles[i]['offset'],oldroles[i]['time'],oldroles[i]['helper'])):
            z=roles[i];z['helper']=assigned_h[i];z['width']=assigned_w[i];z['offset']=off;off+=z['width']
            matching.append({'stage':z['stage'],'replica':z['replica'],'old_helper':oldroles[i]['helper'],
                             'new_helper':z['helper'],'old_width':oldroles[i]['width'],'new_width':z['width'],
                             'family':z['family'],'child':z['child'],'old_offset':oldroles[i]['offset'],'new_offset':z['offset']})
        assert off==used[g]<=cap[g]
    roles.sort(key=lambda z:(z['time'],z['helper']))
    newused,newfamilies=audit_roles(roles,plan,newwidths,V,R)
    assert newfamilies==oldfamilies
    paid=Counter();remainders=[]
    for c in plan['provider_calls']:paid.update(signatures[c['provider']]['profile'])
    idle=Counter()
    for key,(capacity,window) in plan['windows'].items():
        rep,ch=map(int,key.split(','))
        for port in range(V):
            occupied=len(newused[rep,ch,port]);left=capacity-occupied
            if left:
                family=rep*(8*V)+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*V+port
                remainders.append({'child':ch,'port':port,'replica':rep,'replicas':1,'family':family,
                                   'rank':left,'hosted':occupied,'pending_offset':occupied})
                idle[left]+=1
    paid.update(idle);mass=sum(r*n for r,n in paid.items())
    assert M*plan['live']-mass==plan['deficit']==2560
    assert M*M>2*max(paid)**2
    oldprofile={int(r):n for r,n in plan['profile'].items()}
    ownerraw=packed(roles);gz=bytearray(gzip.compress(ownerraw,mtime=0));gz[9]=255
    (a.out/'OWNERS.json.gz').write_bytes(bytes(gz))
    (a.out/'MATCHING.json.gz').write_bytes(gzip.compress(packed(matching),mtime=0))
    (a.out/'REMAINDERS.json').write_text(json.dumps(remainders,indent=2)+'\n')
    profile=dict(sorted(paid.items()))
    (a.out/'PROFILE.json').write_text(json.dumps(profile,indent=2)+'\n')
    owner_fields={'profile':profile,
                  'per_call_widths':[{'stage':s,'replica':r,'widths':newwidths[s,r]} for s,r in plan['order']],
                  'assignment_sha256':hashlib.sha256(ownerraw).hexdigest(),
                  'assignment_sha256_semantics':'SHA256 of sorted-key compact uncompressed OWNERS array',
                  'source_owners_sha256':sha(a.owners),
                  'provider_signatures':signatures}
    (a.out/'PLAN-OWNER-FIELDS.json').write_text(json.dumps(owner_fields,indent=2)+'\n')
    rec={'status':'PASS_OWNER_REUSE_NOMINATION_COMBINATORICS_NOT_FULL_SUPPLIER_ADMISSION',
         'source_plan':str(a.plan),'source_plan_sha256':sha(a.plan),'source_owners_sha256':sha(a.owners),
         'owners_sha256':sha(a.out/'OWNERS.json.gz'),'unchanged_owner_family_sets':True,
         'unchanged_call_order_and_windows':True,'all_footprints_are_disjoint_compacted_prefixes':True,
         'local_signatures':signatures,'sorted_initial_dominance':dominance,'matching_passes':passes,
         'roles':len(roles),'calls':len(calls),'remainder_children':len(remainders),'remainder_profile':dict(sorted(idle.items())),
         'global_profile':profile,'rank_mass':mass,'deficit':2560,'maxchild':max(paid),
         'source_floating_screen_b':rate(oldprofile,2560,M),
         'candidate_floating_screen_b':rate(profile,2560,M),
         'seconds':time.monotonic()-beg,
         'remaining_admission':'Bind freshly verified provider artifacts and their hashes; regenerate the global template, actual 73-column sigmas and remainder axes with the existing emitter; run independent owner/frame audit, finite invoice, and exact moment/outer assembly.'}
    (a.out/'OWNER-REUSE.json').write_text(json.dumps(rec,indent=2)+'\n')
    print(json.dumps({k:rec[k] for k in ('status','roles','matching_passes','remainder_profile','rank_mass','source_floating_screen_b','candidate_floating_screen_b','seconds')},indent=2),flush=True)


if __name__=='__main__':main()
