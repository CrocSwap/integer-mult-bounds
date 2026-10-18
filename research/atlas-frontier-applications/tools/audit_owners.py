# SPDX-License-Identifier: Apache-2.0
"""Source-event audit derived from PR2848's independently implemented auditor.
Credit Yiyang / Lyy-iiis, OpenAI Codex assistance, and the retained source notices.
Generalized here to any round-robin lift and a changed literal allocation;
imports no producer, candidate generator or inherited owner engine.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse,gzip,hashlib,json

def need(c,m):
    if not c: raise ValueError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def audit(source,candidate):
    pins=read(source/'SOURCE-PINS.json')['files'];raw={}
    for pin in pins:
        need(Path(pin['name']).name==pin['name'],'source basename')
        b=(source/'sources'/pin['name']).read_bytes()
        need(hashlib.sha256(b).hexdigest()==pin['sha256'],'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==pin['git_blob'],'source Git blob')
        raw[pin['name']]=json.loads(gzip.decompress(b) if pin['name'].endswith('.gz') else b) if pin['name'].endswith(('.json','.gz')) else b
    order=read(candidate/'ORDER.json');rows=read(candidate/'FILL.json.gz')['rows'];dr=read(candidate/'DISPATCH.json');dispatch={(s,r):p for s,r,p in dr}
    oldorder=raw['PR2843-ORDER.json'];oldfill=raw['PR2843-FILL.json.gz']['rows'];olddispatch={(s,r):p for s,r,p in raw['PR2843-DISPATCH.json']}
    T=1+max(r for s,r in oldorder);N=1+max(r for s,r in order);need(N%T==0,'integer lift');copies=N//T;calls=9*N
    need(copies>=1 and order==[[s,r+T*g]for s,r in oldorder for g in range(copies)],'exact round-robin source call lift')
    need(len(dr)==len(dispatch)==calls and dispatch=={(s,r+T*g):p for (s,r),p in olddispatch.items()for g in range(copies)},'exact provider lift')
    expected=[[copies*t+g,h,o+T*g,c,p,z]for t,h,o,c,p,z in oldfill for g in range(copies)]
    need(len(rows)==len(expected)==408*calls,'complete role count')
    changes=[{'before':a,'after':b}for a,b in zip(expected,rows)if a!=b]
    template=raw['PR2833-T37-TEMPLATE.json.gz'];plan=raw['PR2833-PLAN.json'];providers=raw['PR2833-PROVIDERS.json']
    blocks={};stage=None;tail=[]
    for ix,e in enumerate(template['execution_schedule']):
        if e['kind'] in ('bank_padding_cover_sweep','translate_every_live_family'):tail.append(ix);continue
        if e['kind']=='local_cover_sweep':stage=e['stage'];blocks[stage]=[]
        need(stage is not None,'leading source event');blocks[stage].append((ix,e))
    need(tail==[30,31],'exact source terminal events')
    pair={e['stage']:e['pair']for e in template['recipe']if e['kind']=='local'};caps={}
    for e in template['idle_children']:
        need(e['child'] not in caps or caps[e['child']]==e['rank'],'consistent capacity');caps[e['child']]=e['rank']
    last={};windows={};callclock=[];projection=defaultdict(list);clock=0
    for t,(stage,replica) in enumerate(order):
        for ix,e in blocks[stage]:
            projection[replica].append(ix)
            if e['kind']=='local_cover_sweep':last[replica,pair[stage]]=clock;callclock.append(clock)
            elif e['kind']=='bridge':last[replica,e['src']]=clock;last[replica,e['dst']]=clock
            elif e['kind']=='idle_cover_sweep':
                for child in e['child_indices']:
                    if child in caps:windows[replica,child]=(last.get((replica,e['pair']),-1),clock)
            clock+=1
    need(len(projection)==N and all(v==list(range(30))for v in projection.values()),'every ordered source projection')
    need(len(callclock)==calls,'exact local event count')
    masks={};helpers=[0]*calls;families=[set() for _ in order]
    for row in rows:
        need(type(row) is list and len(row)==6 and all(type(v)is int for v in row),'integer role')
        t,h,o,c,p,z=row;need(0<=t<calls and 0<=h<408 and 0<=o<N and 0<=p<112 and z>=0,'role range')
        width=providers[dispatch[tuple(order[t])]]['widths'][h];begin,end=windows[o,c]
        need(begin<callclock[t]<end,'strict source-event window')
        family=o*896+(2*plan['pairs'][str(c)]+plan['sides'][str(c)])*112+p
        need(family not in families[t],'physical family collision');families[t].add(family)
        need(not (helpers[t]>>h)&1,'duplicate helper');helpers[t]|=1<<h
        key=o,c,p;bits=((1<<width)-1)<<z
        need(z+width<=caps[c],'capacity');need(not masks.get(key,0)&bits,'mask overlap');masks[key]=masks.get(key,0)|bits
    need(all(v==(1<<408)-1 for v in helpers),'all actual helpers in every call')
    idle=Counter()
    for o in range(N):
        for c,cap in caps.items():
            for p in range(112):
                mask=masks.get((o,c,p),0);need(not mask&(mask+1),'compact used prefix');rem=cap-mask.bit_count()
                if rem:idle[rem]+=1
    profile=Counter(idle)
    for call in order:
        for rank,n in providers[dispatch[tuple(call)]]['actual_paid_profile'].items():profile[int(rank)]+=n
    claimed={int(k):v for k,v in read(candidate/'PROFILE.json').items()};need(dict(profile)==claimed,'complete paid histogram')
    need(sum(k*v for k,v in profile.items())==N*(896*73-320),'exact rank mass')
    return dict(status='PASS_SEPARATE_SOURCE_EVENT_AND_LITERAL_OWNER_AUDIT',replicas=N,copies=copies,calls=calls,roles=len(rows),changes=changes,idle=dict(sorted(idle.items())),profile=dict(sorted(profile.items())),rank_mass=sum(k*v for k,v in profile.items()),live=N*896,source_event_positions_first_10=callclock[:10],input_sha256={n:sha(candidate/n)for n in ['FILL.json.gz','ORDER.json','DISPATCH.json','PROFILE.json']},source_pin_sha256=sha(source/'SOURCE-PINS.json'),scope='Complete finite owner/source-event/profile check; native, precision, outer and all-size assumptions are separate.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-package',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();result=audit(a.source_package,a.candidate);need(not a.out.exists(),'fresh audit output');a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:result[k]for k in ['status','replicas','roles','calls','rank_mass','live','changes']},indent=2))
