#!/usr/bin/env python3
"""Preserve PR569 geometry by bijectively relabeling equal-width helpers."""
import argparse,copy,gzip,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path


def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(b,s):
    if not b:raise ValueError(s)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ('plan','owners','local','out'):ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();require(not a.out.exists(),'Fresh output directory required')
    plan,owners=read(a.plan),read(a.owners);word=read(a.local/'CANONICAL-WORD.json.gz');checks=read(a.local/'LOCAL-CHECKS.json')
    pid='width7_eight';desc=plan['provider_registry'][pid];old=desc['widths'];new=[9-len(word['frames'][f])for f in word['start'][224:]]
    require(Counter(old)==Counter(new),'Inventories differ')
    require(word['ports']==desc['ports'] and word['centers']==desc['centers'],'Interface differs')
    perm={h:h for h in range(504)if old[h]==new[h]}
    for width in sorted(set(old)):
        source=[h for h in range(504)if old[h]==width and h not in perm]
        target=[h for h in range(504)if new[h]==width and h not in perm.values()]
        require(len(source)==len(target),'Unmatched width slots')
        perm.update(zip(source,target))
    require(set(perm)==set(perm.values())==set(range(504)),'Not a helper bijection')
    source_rows=copy.deepcopy(owners);count=0
    for row in owners:
        call=plan['provider_calls'][row['time']]
        if call['provider']==pid:
            row['helper']=perm[row['helper']];count+=1
        width=new[row['helper']]if call['provider']==pid else plan['provider_registry'][call['provider']]['widths'][row['helper']]
        require(row['width']==width,'Assigned slot has wrong width')
    require(all({k:v for k,v in x.items()if k!='helper'}=={k:v for k,v in y.items()if k!='helper'}for x,y in zip(source_rows,owners)),'Physical geometry changed')
    bycall=defaultdict(list)
    for row in owners:bycall[row['time']].append(row)
    require(all({r['helper']for r in bycall[t]}==set(range(504))and len({r['family']for r in bycall[t]})==504 for t in range(72)),'Wrong complete owner call')
    desc['widths']=new;desc['actual_paid_profile']=checks['forward']['paid_profile']
    require(checks['forward']['paid_profile']==checks['backward']['paid_profile'],'Orientation mismatch')
    desc['orientation_program_sha256']={n:v['sha256']for n,v in checks.items()}
    desc['artifact_sha256']={n:sha(a.local/n)for n in desc['artifact_sha256']if(a.local/n).is_file()}
    paid=Counter()
    for call in plan['provider_calls']:
        d=plan['provider_registry'][call['provider']];paid.update({int(k):v for k,v in d['actual_paid_profile'].items()})
        call['local_program_sha256']=d['orientation_program_sha256'][call['orientation']]
    for call in plan['per_call_widths']:
        chosen=next(c for c in plan['provider_calls']if(c['stage'],c['replica'])==(call['stage'],call['replica']))
        call['widths']=plan['provider_registry'][chosen['provider']]['widths']
    bins=defaultdict(set)
    for row in owners:
        key=row['owner_replica'],row['child'],row['port'];cells=set(range(row['offset'],row['offset']+row['width']))
        require(not bins[key]&cells,'Overlapping physical footprint');bins[key]|=cells
        cap,window=plan['windows'][f'{key[0]},{key[1]}'];require(row['time']in window and min(cells)>=0 and max(cells)<cap,'Invalid physical window')
    idle=Counter()
    for key,(cap,_)in plan['windows'].items():
        r,c=map(int,key.split(','))
        for port in range(112):
            cells=bins[r,c,port];require(cells==set(range(len(cells))),'Nonprefix owner')
            if len(cells)<cap:idle[cap-len(cells)]+=1
    paid.update(idle);require(sum(k*v for k,v in paid.items())==520704,'Wrong rank mass')
    a.out.mkdir();owners.sort(key=lambda r:(r['time'],r['helper']))
    data=gzip.compress(json.dumps(owners,sort_keys=True,separators=(',',':')).encode(),mtime=0);data=data[:9]+b'\xff'+data[10:]
    (a.out/'OWNERS.json.gz').write_bytes(data)
    plan.update(status='PENDING_COMBINED_PREFIX_PHASE_AND_PHYSICAL_ADMISSION',profile=dict(sorted(paid.items())),source_plan_sha256=sha(a.plan),source_owners_sha256=sha(a.owners),assignment_sha256=sha(a.out/'OWNERS.json.gz'))
    (a.out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
    receipt=dict(status='PASS_EXACT_HELPER_BIJECTION_WITH_UNCHANGED_PHYSICAL_GEOMETRY',source_plan_sha256=sha(a.plan),source_owners_sha256=sha(a.owners),new_plan_sha256=sha(a.out/'PLAN.json'),new_owners_sha256=sha(a.out/'OWNERS.json.gz'),replacement_canonical_sha256=sha(a.local/'CANONICAL-WORD.json.gz'),profile=dict(sorted(paid.items())),idle_remainders=dict(sorted(idle.items())),helper_bijection=perm,changed_helper_labels={h:k for h,k in perm.items()if h!=k},selected_calls=count//504,scope='Literal whole-owner geometry, windows, offsets and width of every slot are unchanged; only helper labels are permuted within each complete selected call. New local phase, independent physical replay, fresh invoice and exact outer admission remain separate.')
    (a.out/'NOMINATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k]for k in('profile','idle_remainders','changed_helper_labels','selected_calls')},indent=2))

if __name__=='__main__':main()
