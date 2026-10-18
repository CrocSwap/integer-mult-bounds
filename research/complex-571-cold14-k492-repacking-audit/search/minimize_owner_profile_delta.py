"""Reduce a candidate's changed placements, preserving every owner's exact load.

Discovery only: unchanged downstream physical and arithmetic admission required.
Prepared with OpenAI Codex assistance.
"""
import argparse, copy, gzip, hashlib, json
from collections import defaultdict, Counter
from pathlib import Path
from ortools.sat.python import cp_model

def main():
    if not __debug__: raise RuntimeError('Assertions required for candidate export')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,default=30)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    read=lambda d:json.loads(gzip.decompress((d/'OWNERS.json.gz').read_bytes()))
    base=read(a.base);candidate=read(a.candidate);plan=json.loads((a.candidate/'PLAN.json').read_bytes())
    base.sort(key=lambda r:(r['time'],r['helper']));candidate.sort(key=lambda r:(r['time'],r['helper']))
    key=lambda r:(r['owner_replica'],r['child'],r['port'])
    model=cp_model.CpModel();xs={};loads=defaultdict(list);limits=defaultdict(int);families=defaultdict(list)
    for i,(old,new) in enumerate(zip(base,candidate)):
        assert (old['time'],old['helper'],old['width'])==(new['time'],new['helper'],new['width'])
        limits[key(new)]+=new['width']
        if key(old)==key(new):
            loads[key(new)].append(new['width']);families[new['family'],new['time']].append(1)
        else:
            x=xs[i]=model.new_bool_var(str(i));model.add_hint(x,1)
            loads[key(old)].append(old['width']*(1-x));loads[key(new)].append(new['width']*x)
            families[old['family'],old['time']].append(1-x);families[new['family'],new['time']].append(x)
    capacities={}
    for label,(cap,times)in plan['windows'].items():
        o,ch=map(int,label.split(','))
        for port in range(112):capacities[o,ch,port]=cap
    target=Counter(cap-limits[k]for k,cap in capacities.items())
    dynamic={key(base[i])for i in xs}|{key(candidate[i])for i in xs}
    fixed=Counter(cap-limits[k]for k,cap in capacities.items()if k not in dynamic)
    needed=target-fixed;indicators=defaultdict(list)
    for k in dynamic:
        choices=[];cap=capacities[k]
        for r in needed:
            if r>cap:continue
            z=model.new_bool_var(f'rem{k}_{r}');choices.append(z);indicators[r].append(z)
            model.add(sum(loads[k])==cap-r).only_enforce_if(z)
            model.add_hint(z,int(cap-limits[k]==r))
        model.add_exactly_one(choices)
    for r,terms in indicators.items():model.add(sum(terms)==needed[r])
    for terms in families.values():model.add(sum(terms)<=1)
    model.minimize(sum(xs.values()));solver=cp_model.CpSolver()
    solver.parameters.num_search_workers=2;solver.parameters.max_time_in_seconds=a.seconds
    status=solver.solve(model);assert status in (cp_model.OPTIMAL,cp_model.FEASIBLE)
    result=[dict(candidate[i] if i in xs and solver.value(xs[i]) else r)for i,r in enumerate(base)]
    bins=defaultdict(list);seen=set();moves=[]
    for old,r in zip(base,result):
        assert (r['family'],r['time'])not in seen;seen.add((r['family'],r['time']))
        bins[key(r)].append(r)
        if key(old)!=key(r):moves.append(dict(time=r['time'],helper=r['helper'],width=r['width'],before=list(key(old)),after=list(key(r))))
    for k,rs in bins.items():
        off=0;cap,times=plan['windows'][f'{k[0]},{k[1]}']
        for r in rs:
            assert r['time'] in times;r['offset']=off;off+=r['width']
        assert off<=cap
    actual=Counter(cap-sum(r['width']for r in bins[k])for k,cap in capacities.items());assert actual==target
    raw=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    plan['assignment_sha256']=hashlib.sha256(raw).hexdigest();plan['mode']='minimal-delta-owner-repacking'
    (a.out/'OWNERS.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    (a.out/'PLAN.json').write_text(json.dumps(plan,indent=1)+'\n')
    report=dict(model='old_or_proposed_owner_with_fixed_idle_profile',status=solver.status_name(status),original_changed=len(xs),changed=len(moves),seconds=solver.wall_time,moves=moves)
    (a.out/'MOVES.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='moves'}),flush=True)

if __name__=='__main__': main()
