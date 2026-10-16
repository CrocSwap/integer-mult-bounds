# SPDX-License-Identifier: Apache-2.0
"""Source-event audit derived from PR2848's independently implemented auditor.
Credit Yiyang / Lyy-iiis, OpenAI Codex assistance, and the retained source notices.
Generalized here to a pinned PR2857 baseline, its round-robin chronology lifts and a changed literal
allocation (preload-move words: the provider widths are DERIVED from the shipped words, not read from
the PR2857 registry, and the shipped registry must equal them); imports no producer, candidate
generator or inherited owner engine.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse,gzip,hashlib,json

def need(c,m):
    if not c: raise ValueError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def basis(vs):
    piv={}
    for a in vs:
        while a:
            bit=a.bit_length()-1
            if bit in piv:a^=piv[bit]
            else:piv[bit]=a;break
    for k in sorted(piv):
        for j in piv:
            if j>k and piv[j]>>k&1:piv[j]^=piv[k]
    return tuple(piv[k] for k in sorted(piv,reverse=True))
def derive_providers(words):
    out={}
    for pid,tag in (('gauge44','base'),('extra','extra')):
        w=read(words/('WORD-PM-'+tag+'.json.gz'));live=sorted(set(range(224,704))-set(w['removed']));need(len(live)==408,'408 live helpers')
        out[pid]=dict(widths=[len(basis(w['helper_final'].get(str(r),[256,128,64,32,16,8,4,2,1])))-len(basis(w['start_extra'].get(str(r),[]))) for r in live],actual_paid_profile=w['report']['local_profile'])
    return out
def audit(source,candidate,words):
    pins={'CLAIM.json': 'c2a04b639c86f462caef654a29817545c57b8e5ba809e37d4d476d3577f5cd6f', 'DISPATCH.json': '5513481a70c83767b5836b15fb7ff204d2a8f8fca83c6bcaee90a20b3d1ec6c4', 'FILL.json.gz': '82218aaaf08825bd4a3cca676815c7e9c00d06d0da123b1c5ad234c8c91cb501', 'ORDER.json': '84f030a59dde4fa4635988ef0931ebae66964b3a202df79d38247fbe8a5592dc', 'PROFILE.json': 'f5d91190e5a062585a99c3959615b837271feca987eed04ae7d707d5714b17aa', 'PROVIDERS.json': 'b1e31d1b3af2c8db9b8dd8f1337fee7fc2570ee58c1d541c43963c640efa1aa2', 'sources/PR2833-PLAN.json.gz': 'd566cfb87b71639d4138e1f89b543e2dd6a7772070226a2a14c799a6835bf21e', 'sources/PR2833-T37-TEMPLATE.json.gz': '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'}
    def inventory():
        need(all(sha(source/n)==h for n,h in pins.items()),'pinned complete owner-source inputs changed')
    inventory()
    raw={}
    raw['BASE-ORDER']=read(source/'ORDER.json')
    raw['BASE-FILL']=read(source/'FILL.json.gz')
    raw['BASE-DISPATCH']=read(source/'DISPATCH.json')
    raw['SOURCE-TEMPLATE']=read(source/'sources/PR2833-T37-TEMPLATE.json.gz')
    raw['SOURCE-PLAN']=read(source/'sources/PR2833-PLAN.json.gz')
    raw['PROVIDERS']=read(candidate/'PROVIDERS.json');need(raw['PROVIDERS']==derive_providers(words),'shipped provider registry equals the widths and paid profile derived from the shipped words')
    need(raw['PROVIDERS']['gauge44']['widths']==raw['PROVIDERS']['extra']['widths'],'common helper widths')
    order=read(candidate/'ORDER.json');rows=read(candidate/'FILL.json.gz')['rows'];dr=read(candidate/'DISPATCH.json');dispatch={(s,r):p for s,r,p in dr}
    oldorder=raw['BASE-ORDER'];oldfill=raw['BASE-FILL']['rows'];olddispatch={(s,r):p for s,r,p in raw['BASE-DISPATCH']}
    T=1+max(r for s,r in oldorder);N=1+max(r for s,r in order);need(N%T==0,'integer lift');copies=N//T;calls=9*N
    need(copies>=1 and order==[[s,r+T*g]for s,r in oldorder for g in range(copies)],'exact round-robin source call lift')
    need(len(dr)==len(dispatch)==calls and dispatch=={(s,r+T*g):p for (s,r),p in olddispatch.items()for g in range(copies)},'exact provider lift')
    need(len(rows)==408*calls,'complete role count')
    template=raw['SOURCE-TEMPLATE'];plan=raw['SOURCE-PLAN'];providers=raw['PROVIDERS']
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
    inventory()
    return dict(status='PASS_SEPARATE_SOURCE_EVENT_AND_LITERAL_OWNER_AUDIT',replicas=N,copies=copies,calls=calls,roles=len(rows),idle=dict(sorted(idle.items())),profile=dict(sorted(profile.items())),rank_mass=sum(k*v for k,v in profile.items()),live=N*896,source_event_positions_first_10=callclock[:10],input_sha256={n:sha(candidate/n)for n in ['FILL.json.gz','ORDER.json','DISPATCH.json','PROFILE.json']},source_pin_sha256=sha(source/'CLAIM.json'),scope='Complete finite owner/source-event/profile check; native, precision, outer and all-size assumptions are separate.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-package',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--words',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();result=audit(a.source_package,a.candidate,a.words.resolve());need(not a.out.exists(),'fresh audit output');a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:result[k]for k in ['status','replicas','roles','calls','rank_mass','live','idle']},indent=2))
