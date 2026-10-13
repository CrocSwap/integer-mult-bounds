#!/usr/bin/env python3
"""Nominate PR568/569 composition by shortening the retained literal owners.

The whole family and invocation assignment is unchanged. Residual cells in
one pending block are compacted in old offset order. This is a literal map
proposal; independent physical/phase/invoice admission remains required.
"""
import argparse
from collections import Counter,defaultdict
import gzip,hashlib,importlib.util,json
from pathlib import Path


def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(b,s):
    if not b:raise ValueError(s)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ('plan','owners','plain','combined','engine','out'):ap.add_argument('--'+key,type=Path,required=True)
    a=ap.parse_args();require(not a.out.exists(),'Fresh output required')
    plan,roles=read(a.plan),read(a.owners);profiles={};widths={}
    for pid,path in [('fourcold_eight',a.plain),('width7_eight',a.combined)]:
        word=read(path/'CANONICAL-WORD.json.gz');audit=read(path/'SCALAR-FRAME-AUDIT.json')
        require(audit['status']=='PASS_CHANGED_WORD_ALL_COLUMNS_AND_NATIVE_FRAMES','Native check missing')
        profiles[pid]={int(k):v for k,v in word['local_profile'].items()}
        widths[pid]=[9-len(word['frames'][fr]) for fr in word['start'][224:]]
    bins=defaultdict(list);changes=[];paid=Counter();helpers=defaultdict(set);families=defaultdict(set)
    for row in roles:bins[row['owner_replica'],row['child'],row['port']].append(row)
    for call in plan['provider_calls']:paid.update(profiles[call['provider']])
    idle=Counter()
    for key,(cap,window) in plan['windows'].items():
        replica,child=map(int,key.split(','))
        for port in range(112):
            offset=0
            for row in sorted(bins[replica,child,port],key=lambda r:r['offset']):
                time,helper=row['time'],row['helper'];pid=plan['provider_calls'][time]['provider'];new=widths[pid][helper]
                require(new<=row['width'],'Residual got larger')
                if new!=row['width']:changes.append([time,helper,row['width'],new])
                row['offset'],row['width']=offset,new;offset+=new
                require(time in window and offset<=cap,'Window/footprint failed')
                require(helper not in helpers[time] and row['family']not in families[time],'Duplicate owner/helper')
                helpers[time].add(helper);families[time].add(row['family'])
            if offset<cap:idle[cap-offset]+=1
    require(len(changes)==288 and {h for _,h,_,_ in changes}=={271,283,295,307},'Wrong four extra residuals')
    require(all(helpers[t]==set(range(504))for t in range(72)),'Incomplete calls')
    paid.update(idle);require(sum(k*v for k,v in paid.items())==520704,'Wrong total rank mass')
    spec=importlib.util.spec_from_file_location('exact_moment',a.engine);engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    price=engine.certify(paid,73,7168,False)
    a.out.mkdir(parents=True)
    raw=json.dumps(roles,sort_keys=True,separators=(',',':')).encode();packed=gzip.compress(raw,mtime=0);packed=packed[:9]+b'\xff'+packed[10:]
    (a.out/'OWNERS.json.gz').write_bytes(packed)
    result=dict(status='PASS_LITERAL_COMPACTED_NOMINATION_PENDING_ADMISSION',source_plan_sha256=sha(a.plan),source_owners_sha256=sha(a.owners),new_owners_sha256=sha(a.out/'OWNERS.json.gz'),profile=dict(sorted(paid.items())),idle_remainders=dict(sorted(idle.items())),changed_residuals=changes,nominal_price=price,scope='Exact literal widths, prefix compaction, unchanged whole-owner families/calls, windows and rank mass checked. Native provider all-column/frame checks passed. Complete phase, independent physical replay, fresh invoice and outer assembly remain required.')
    (a.out/'NOMINATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ('profile','idle_remainders','nominal_price')},indent=2))

if __name__=='__main__':main()
