#!/usr/bin/env python3
"""Independent exact literal U-conditional replay; no physical/price claim."""
import argparse
import bisect
import collections
from fractions import Fraction as F
import gzip
import hashlib
import json
import math
from pathlib import Path

SOURCE_GZ='2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c'
SOURCE_CAN='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d'
PATCH={
38486:(['MOVE',902,3,595,False],['MOVE',902,3,373,False]),
38487:(['ADD',1532,902,'2',595],None),
38785:(['ADD',1479,902,'-1/2',595],None),
38786:(['ADD',1255,902,'-1',595],None),
38787:(['ADD',1495,902,'-3/2',595],None),
38788:(['MOVE',1091,373,618,False],None),
38789:(['MOVE',902,595,618,False],None),
38790:(['ADD',1091,902,'1/2',618],['ADD',1091,902,'1/2',373]),
38813:(['MOVE',1091,618,733,False],['MOVE',1091,373,733,False]),
41448:(['MOVE',902,618,913,False],['MOVE',902,373,913,False])}


INCIDENTS=[(37803,['ADD',1091,1097,'1/2',373]),(38482,['ADD',643,902,'-1/4',3]),(38483,['ADD',496,902,'-1/2',3]),(38484,['ADD',1466,902,'1/2',3]),(38485,['ADD',450,902,'-1/2',3]),(38486,['MOVE',902,3,595,False]),(38487,['ADD',1532,902,'2',595]),(38785,['ADD',1479,902,'-1/2',595]),(38786,['ADD',1255,902,'-1',595]),(38787,['ADD',1495,902,'-3/2',595]),(38788,['MOVE',1091,373,618,False]),(38789,['MOVE',902,595,618,False]),(38790,['ADD',1091,902,'1/2',618]),(38813,['MOVE',1091,618,733,False]),(38815,['ADD',1091,1093,'-1',733]),(38941,['MOVE',1091,733,238,False]),(38943,['ADD',1091,1087,'1',238]),(41448,['MOVE',902,618,913,False]),(41449,['ADD',985,902,'-1',913])]

class Refusal(Exception):
    def __init__(self,reason,**detail): super().__init__(reason);self.reason=reason;self.detail=detail

def need(ok,reason,**detail):
    if not ok: raise Refusal(reason,**detail)
def sha(b): return hashlib.sha256(b).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def load(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)
def pack(row): return {str(k):str(v) for k,v in sorted(row.items()) if v}
def span(vectors):
    s={0}
    for v in vectors:
        need(type(v) is int and 0<v<512 and v not in s,'frame_invalid',vector=v)
        s |= {x^v for x in tuple(s)}
    return frozenset(s)

class Grid:
    def __init__(self): self.twos=0;self.odd_lcm=1;self.bits=0;self.count=0
    def note(self,q):
        q=F(q);d=q.denominator;v=(d&-d).bit_length()-1;odd=d>>v;remain=odd
        for p in (3,5):
            while remain%p==0: remain//=p
        need(remain==1,'nonsmooth_denominator',denominator=d)
        self.twos=max(self.twos,v);self.odd_lcm=math.lcm(self.odd_lcm,odd);self.bits=max(self.bits,abs(q.numerator).bit_length());self.count+=1
    def result(self): return {'max_den_exp':self.twos,'odd_den_lcm':self.odd_lcm,'max_num_bits':self.bits,'values_noted':self.count}

class Replay:
    def __init__(self,w,origins,reverse,side):
        self.w=w;self.origins=origins;self.reverse=reverse;self.side=side
        self.n=w['public'];self.N=self.n+w['owned_fields']
        need((self.n,self.N)==(1501,1569),'dimensions')
        self.sp=[span(f) for f in w['frames']]
        # Every private entry is an independent dirty variable until its INIT.
        self.rows=[{i:F(1)} for i in range(self.N)]
        self.cur=list(w['initial'])+[None]*(self.N-self.n)
        self.alive=set();self.occ=collections.Counter();self.peak=0;self.labels=set()
        self.clears=[];self.interfaces=[];self.guards=[];self.owned_stream=[];self.routes=collections.defaultdict(list)
        self.lit=Grid();self.trajectory=Grid()
        for r in self.rows:
            for v in r.values():self.trajectory.note(v)
    def at(self,role,clock):
        need(type(role) is int and 0<=role<self.N,'bad_operand',side=self.side,clock=clock,role=role)
        need(role<self.n or role in self.alive,'owned_not_live',side=self.side,clock=clock,role=role)
    def chart(self,c,clock): need(type(c) is int and 0<=c<len(self.sp),'bad_chart',side=self.side,clock=clock,chart=c)
    def life(self,r): return self.occ[r] if r>=self.n else None
    def clock(self,j):
        orig=self.origins[j];return {'original_clock':orig,'candidate_clock':self.reverse[orig]}
    def snapshot(self,e,orig,cand,virtual=False):
        op,d=e[:2];src=e[2] if op in ('ADD','COPY') else None
        self.at(d,orig)
        if src is not None:self.at(src,orig)
        chart=e[4] if src is not None else e[3]
        need(virtual or (self.cur[d]==chart and (src is None or self.cur[src]==chart)),'interface_coframe',origin=orig)
        return {'original_clock':orig,'candidate_clock':cand,'event':e,'dest':d,'source':src,'dest_lifetime':self.life(d),'source_lifetime':self.life(src) if src is not None else None,'chart':chart,'actual_dest_chart':self.cur[d],'actual_source_chart':self.cur[src] if src is not None else None,'dest_before':pack(self.rows[d]),'source_before':pack(self.rows[src]) if src is not None else None}
    def step(self,j,e):
        c=self.clock(j);i=c['original_clock'];need(isinstance(e,list) and len(e)>=2,'bad_event',clock=i);op,r=e[:2]
        need(type(r) is int and 0<=r<self.N,'bad_role',clock=i)
        if op=='INIT':
            need(len(e)==3 and r>=self.n and r not in self.alive,'invalid_init',clock=i);self.chart(e[2],i)
            self.alive.add(r);self.labels.add(r);self.occ[r]+=1;self.rows[r]={};self.cur[r]=e[2];self.peak=max(self.peak,len(self.alive))
            self.owned_stream.append({**c,'op':op,'owner':r,'lifetime':self.occ[r],'chart':e[2]})
        elif op=='CLEAR':
            need(len(e)==3 and r>=self.n and r in self.alive and self.cur[r]==e[2],'invalid_clear',clock=i)
            self.clears.append({**c,'owner':r,'lifetime':self.occ[r],'chart':self.cur[r],'row':pack(self.rows[r])})
            self.owned_stream.append({**c,'op':op,'owner':r,'lifetime':self.occ[r],'chart':self.cur[r]})
            self.alive.remove(r);self.rows[r]={};self.cur[r]=None
        elif op=='MOVE':
            need(len(e)==5,'bad_move',clock=i);a,b,flag=e[2:];self.at(r,i);self.chart(a,i);self.chart(b,i)
            need(type(flag) is bool and flag==(r>=self.n) and self.cur[r]==a,'move_owner_or_coframe',clock=i)
            need((self.sp[a]<self.sp[b] or self.sp[b]<self.sp[a]) if flag else self.sp[a]<self.sp[b],'move_not_strict_nested',clock=i)
            self.routes[r].append([a,b]);self.cur[r]=b
            if flag:self.owned_stream.append({**c,'op':op,'owner':r,'lifetime':self.occ[r],'from':a,'to':b})
        elif op in ('ADD','COPY','SCALE'):
            need(len(e)==(4 if op=='SCALE' else 5),'scalar_shape',clock=i);self.at(r,i)
            s=None if op=='SCALE' else e[2]
            if s is not None:self.at(s,i);need(s!=r,'self_scalar',clock=i)
            q=F(e[2] if s is None else e[3]);chart=e[3] if s is None else e[4]
            self.chart(chart,i);need(q!=0 and self.cur[r]==chart and (s is None or self.cur[s]==chart),'scalar_coframe_or_zero',clock=i)
            self.lit.note(q)
            item=self.snapshot(e,i,c['candidate_clock']) if r>=self.n or (s is not None and s>=self.n) else None
            if op=='COPY':
                self.guards.append({**c,'dest':r,'source':s,'chart':chart,'row':pack(self.rows[r]),'dest_lifetime':self.life(r),'source_lifetime':self.life(s)})
                need(not self.rows[r],'copy_nonzero',clock=i)
            if op=='SCALE': self.rows[r]={k:v*q for k,v in self.rows[r].items() if v*q}
            else:
                result=self.rows[r].copy()
                for k,v in self.rows[s].items():
                    val=result.get(k,F(0))+q*v
                    if val:result[k]=val
                    else:result.pop(k,None)
                self.rows[r]=result
            for val in self.rows[r].values():self.trajectory.note(val)
            if item is not None:item['dest_after']=pack(self.rows[r]);self.interfaces.append(item)
        else:raise Refusal('unknown_event',clock=i,opcode=op)
    def finish(self):
        need(not self.alive,'owned_live_at_end');need(self.cur[:self.n]==self.w['final'],'final_charts')
        need(len(self.clears)==167 and self.N-self.n==68 and self.peak==50,'lifetime_counts',clears=len(self.clears),declared_labels=self.N-self.n,used_labels=len(self.labels),peak=self.peak)
        return {'endpoint_rows':[pack(x) for x in self.rows],'end_charts':self.cur,'clears':self.clears,'interfaces':self.interfaces,'copy_guards':self.guards,'owned_stream':self.owned_stream,'routes':{str(k):v for k,v in sorted(self.routes.items())},'peak':self.peak,'owned_labels':sorted(self.labels),'grid':{'literal':self.lit.result(),'trajectory':self.trajectory.result()}}

def census(w,replay):
    ranks=[len(x) for x in w['frames']];paid=collections.Counter();rise=collections.Counter()
    for e in w['program']:
        if e[0]=='MOVE':
            paid[abs(ranks[e[3]]-ranks[e[2]])]+=1
            if e[1]>=w['public'] and ranks[e[3]]>ranks[e[2]]:rise[ranks[e[3]]-ranks[e[2]]]+=1
    live=set(w['live']);mains=live|{x+112 for x in live}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
    targets=collections.Counter(ranks[w['final'][r]]-ranks[w['initial'][r]] for r in range(w['public']) if r not in mains)
    asdict=lambda h:{str(k):v for k,v in sorted(h.items()) if v}
    return {'events':len(w['program']),'opcodes':dict(sorted(collections.Counter(e[0] for e in w['program']).items())),'native_paid':asdict(paid),'native_targets':asdict(targets),'owned_rises':asdict(rise),'owned_moves':sum(1 for x in replay['owned_stream'] if x['op']=='MOVE'),'lifetimes':len(replay['clears']),'peak':replay['peak']}

def difference(a,b): return {k:b.get(k,0)-a.get(k,0) for k in sorted(set(a)|set(b),key=int) if b.get(k,0)!=a.get(k,0)}

def run(root,built):
    op=root/'inputs/pr7620/data/word.json.gz';bp=built/'candidate-word.json.gz';mp=built/'edit-manifest.json'
    need(sha(op.read_bytes())==SOURCE_GZ,'source_gzip_hash');old=load(op);new=load(bp);manifest=load(mp);status=load(built/'status.json')
    need(sha(canon(old))==SOURCE_CAN,'source_canonical_hash');need(status['status']=='CANDIDATE_BUILT_UNQUALIFIED','builder_status')
    csha=sha(canon(new));gzsha=sha(bp.read_bytes());meta=sha(canon({k:v for k,v in old.items() if k!='program'}))
    need(manifest['schema']=='compose7620-edit-manifest/v1' and manifest['source_canonical_sha256']==SOURCE_CAN and manifest['source_gzip_sha256']==SOURCE_GZ and manifest['source_git_blob']=='2b8a259e017748ab5a3b98c22b42b8d3113edfce' and manifest['candidate_canonical_sha256']==status['candidate_canonical_sha256']==csha and manifest['candidate_gzip_sha256']==status['candidate_gzip_sha256']==gzsha and manifest['metadata_sha256']==meta,'manifest_hash_binding')
    def operands(e):
        need(isinstance(e,list) and len(e)>=2,'incident_event_shape')
        if e[0] in ('ADD','COPY'):need(len(e)==5,'incident_scalar_shape');return {e[1],e[2]}
        need(e[0] in ('MOVE','SCALE','INIT','CLEAR'),'incident_opcode');return {e[1]}
    incidents=[(i,old['program'][i]) for i in range(37803,41450) if operands(old['program'][i]) & {902,1091}]
    need(incidents==INCIDENTS,'incident_window_mismatch')
    need(len(old['program'])==77194 and len(new['program'])==77188,'event_count')
    need({k:v for k,v in old.items() if k!='program'}=={k:v for k,v in new.items() if k!='program'},'metadata_changed')
    origins=[];rebuilt=[];reverse=[None]*len(old['program'])
    for i,e in enumerate(old['program']):
        if i in PATCH:
            a,b=PATCH[i];need(e==a,'literal_patch_mismatch',origin=i)
            if b is None:continue
            e=b
        reverse[i]=len(rebuilt);origins.append(i);rebuilt.append(e)
    need(new['program']==rebuilt,'independent_reconstruction_mismatch')
    need(manifest['candidate_origins']==origins and manifest['original_to_candidate']==reverse,'origin_map_mismatch')
    need(manifest['edits']==[{'original_index':i,'old':a,'new_or_null':b} for i,(a,b) in PATCH.items()],'manifest_edits_mismatch')
    oldr=Replay(old,list(range(len(old['program']))),reverse,'original')
    for j,e in enumerate(old['program']):oldr.step(j,e)
    original=oldr.finish()
    newr=Replay(new,origins,reverse,'candidate');virtual=[]
    deleted=[i for i,(a,b) in PATCH.items() if b is None and a[0] in ('ADD','COPY','SCALE') and (a[1]>=1501 or (a[0]!='SCALE' and a[2]>=1501))]
    cuts=collections.defaultdict(list)
    for i in deleted: cuts[bisect.bisect_left(origins,i)].append(i)
    for j in range(len(new['program'])+1):
        for i in cuts.get(j,[]):
            record=newr.snapshot(old['program'][i],i,None,virtual=True);record['candidate_cut']=j;virtual.append(record)
        if j<len(new['program']):newr.step(j,new['program'][j])
    candidate=newr.finish();candidate['virtual_deleted_interfaces']=virtual
    need(original['endpoint_rows']==candidate['endpoint_rows'] and original['end_charts']==candidate['end_charts'],'endpoint_mismatch')
    live=set(old['live']);mains=live|{x+112 for x in live}|set(old['hosted']['X2'])|set(old['hosted']['Y2'])
    for r in range(1501):
        if r not in mains:need(original['endpoint_rows'][r]=={str(r):'1'},'helper_not_identity',role=r)
    def strip_clock(xs):return [{k:v for k,v in x.items() if k!='candidate_clock'} for x in xs]
    need(strip_clock(original['owned_stream'])==strip_clock(candidate['owned_stream']),'owned_stream_changed')
    need(original['owned_labels']==candidate['owned_labels'],'used_owned_label_set_changed')
    need([e['original_clock'] for e in original['clears']]==[e['original_clock'] for e in candidate['clears']],'clear_clock_changed')
    oroutes=original['routes'];nroutes=candidate['routes'];changed_routes=sorted(int(k) for k in set(oroutes)|set(nroutes) if oroutes.get(k,[])!=nroutes.get(k,[]))
    need(changed_routes==[902,1091],'unexpected_changed_routes',roles=changed_routes)
    for mode in ('literal','trajectory'):
        o=original['grid'][mode];n=candidate['grid'][mode]
        need(n['max_den_exp']<=o['max_den_exp']<=25 and n['odd_den_lcm'] and o['odd_den_lcm']%n['odd_den_lcm']==0 and 1125%o['odd_den_lcm']==0 and n['max_num_bits']<=o['max_num_bits'],'grid_increase',mode=mode,original=o,candidate=n)
    oc=census(old,original);nc=census(new,candidate)
    dp=difference(oc['native_paid'],nc['native_paid']);dt=difference(oc['native_targets'],nc['native_targets'])
    need(dp=={'1':-3,'2':1,'4':-1,'5':1} and dt=={} and oc['owned_moves']==nc['owned_moves']==47 and oc['owned_rises']==nc['owned_rises'],'census_mismatch',delta_p=dp,delta_t=dt)
    def changed(o,n,key):
        a={x['original_clock']:x for x in o};b={x['original_clock']:x for x in n};out=[]
        for i in sorted(set(a)|set(b)):
            x=a.get(i);y=b.get(i)
            if x is None or y is None or any(x.get(k)!=y.get(k) for k in key):out.append({'original_clock':i,'original':x,'candidate':y})
        return out
    changes={'clears':changed(original['clears'],candidate['clears'],('owner','lifetime','chart','row')),'interfaces':changed(original['interfaces'],candidate['interfaces'],('event','dest_before','source_before','dest_after')),'copy_guards':changed(original['copy_guards'],candidate['copy_guards'],('dest','source','chart','row'))}
    result={'schema':'compose7620-exact/v1','scope':'Conditional on common U; 1569 dirty entry symbols, literal INIT and CLEAR reset full extent; not a physical or same-premise E7620 acceptance.','source':{'original_canonical_sha256':SOURCE_CAN,'original_gzip_sha256':SOURCE_GZ,'candidate_canonical_sha256':sha(canon(new)),'candidate_gzip_sha256':sha(bp.read_bytes()),'manifest_sha256':sha(mp.read_bytes())},'original':original,'candidate':candidate,'changed':changes,'census':{'original':oc,'candidate':nc,'native_delta_p':dp,'native_delta_t':dt,'seventeen_delta_p':{k:17*v for k,v in dp.items()}}}
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--built',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    try:
        result=run(a.root,a.built);raw=canon(result)
        with (a.out/'EXACT.json.gz').open('wb') as f:
            with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:z.write(raw)
        status={'status':'U_CONDITIONAL_LITERAL_EXACT_ONLY','exact_sha256':sha(raw),'exact_gzip_sha256':sha((a.out/'EXACT.json.gz').read_bytes()),'source':result['source'],'changed_clear_count':len(result['changed']['clears']),'changed_interface_count':len(result['changed']['interfaces']),'limits':result['scope']};code=0
    except Refusal as e:status={'status':'REFUSED','reason':e.reason,'detail':e.detail};code=1
    except Exception as e:status={'status':'REFUSED','reason':'unexpected_exception','type':type(e).__name__,'detail':str(e)};code=1
    (a.out/'status.json').write_text(json.dumps(status,sort_keys=True,indent=2)+'\n');return code
if __name__=='__main__':raise SystemExit(main())
