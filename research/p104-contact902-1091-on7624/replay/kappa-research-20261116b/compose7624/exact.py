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

SOURCE_GZ='bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887'
SOURCE_CAN='c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'
SOURCE_BLOB='81725205c5200d0cf34f9f2debef49d75273e4af'
PATCH={
 38369: (['MOVE',902,3,618,False], ['MOVE',902,3,373,False]),
 38623: (['MOVE',1091,373,618,False], None),
 40279: (['ADD',1091,902,'1/2',618], ['ADD',1091,902,'1/2',373]),
 40280: (['MOVE',1091,618,733,False], ['MOVE',1091,373,733,False]),
 41663: (['MOVE',902,618,913,False], ['MOVE',902,373,913,False]),
}
WINDOW=(37928,41664)
INCIDENTS=[
 (37928,['ADD',1091,1097,'1/2',373]),
 (38365,['ADD',643,902,'-1/4',3]),
 (38366,['ADD',496,902,'-1/2',3]),
 (38367,['ADD',1466,902,'1/2',3]),
 (38368,['ADD',450,902,'-1/2',3]),
 (38369,['MOVE',902,3,618,False]),
 (38623,['MOVE',1091,373,618,False]),
 (40279,['ADD',1091,902,'1/2',618]),
 (40280,['MOVE',1091,618,733,False]),
 (40281,['ADD',1091,1093,'-1',733]),
 (40283,['MOVE',1091,733,238,False]),
 (40285,['ADD',1091,1087,'1',238]),
 (41663,['MOVE',902,618,913,False]),
 (41664,['ADD',985,902,'-1',913]),
]
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
    def __init__(self): self.twos=0;self.odd_lcm=1;self.bits=0;self.count=0;self.nondyadic_count=0
    def note(self,q):
        q=F(q);d=q.denominator;v=(d&-d).bit_length()-1;odd=d>>v;remain=odd
        for p in (3,5):
            while remain%p==0: remain//=p
        need(remain==1,'nonsmooth_denominator',denominator=d)
        self.nondyadic_count+=int(odd!=1);self.twos=max(self.twos,v);self.odd_lcm=math.lcm(self.odd_lcm,odd);self.bits=max(self.bits,abs(q.numerator).bit_length());self.count+=1
    def result(self): return {'max_den_exp':self.twos,'odd_den_lcm':self.odd_lcm,'max_num_bits':self.bits,'values_noted':self.count,'nondyadic_count':self.nondyadic_count}

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
            if op=='COPY':
                need(not self.rows[r],'copy_nonzero',clock=i)
            self.lit.note(q)
            item=self.snapshot(e,i,c['candidate_clock']) if r>=self.n or (s is not None and s>=self.n) else None
            if op=='COPY':
                self.guards.append({**c,'dest':r,'source':s,'chart':chart,'row':pack(self.rows[r]),'dest_lifetime':self.life(r),'source_lifetime':self.life(s)})
            if op=='SCALE': self.rows[r]={k:v*q for k,v in self.rows[r].items() if v*q}
            elif op=='COPY': self.rows[r]={k:v*q for k,v in self.rows[s].items() if v*q}
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
        need(len(self.clears)==204 and self.N-self.n==68 and len(self.labels)==68 and self.peak==50,'lifetime_counts',clears=len(self.clears),declared_labels=self.N-self.n,used_labels=len(self.labels),peak=self.peak)
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
    return {'events':len(w['program']),'opcodes':dict(sorted(collections.Counter(e[0] for e in w['program']).items())),'native_paid':asdict(paid),'native_targets':asdict(targets),'owned_rises':asdict(rise),'owned_moves':sum(1 for x in replay['owned_stream'] if x['op']=='MOVE'),'lifetimes':len(replay['clears']),'peak':replay['peak'],'nondyadic_literal_events':replay['grid']['literal']['nondyadic_count']}

def difference(a,b): return {k:b.get(k,0)-a.get(k,0) for k in sorted(set(a)|set(b),key=int) if b.get(k,0)!=a.get(k,0)}

def source_grid_contract(original,candidate,expected_nondyadic=5901):
    old=original['grid'];new=candidate['grid']
    need(old['trajectory']['odd_den_lcm']==new['trajectory']['odd_den_lcm'],'trajectory_odd_lcm_changed',original=old['trajectory']['odd_den_lcm'],candidate=new['trajectory']['odd_den_lcm'])
    counts=(old['literal']['nondyadic_count'],new['literal']['nondyadic_count'])
    need(counts==(expected_nondyadic,expected_nondyadic),'nondyadic_literal_event_count',original=counts[0],candidate=counts[1],expected=expected_nondyadic)

def validate_maps(manifest,n,deleted):
    need(type(n) is int and n>1 and type(deleted) is int and 0<=deleted<n,'map_bounds')
    origins=manifest.get('candidate_origins');reverse=manifest.get('original_to_candidate');edits=manifest.get('edits')
    need(isinstance(origins,list) and len(origins)==n-1 and isinstance(reverse,list) and len(reverse)==n and isinstance(edits,list),'map_shape')
    for v in origins:need(type(v) is int and 0<=v<n,'origin_type_or_bounds')
    for i,v in enumerate(reverse):
        if i==deleted:need(v is None,'map_deleted_slot')
        else:need(type(v) is int and 0<=v<n-1,'reverse_type_or_bounds')
    for e in edits:
        need(isinstance(e,dict) and type(e.get('original_index')) is int and 0<=e['original_index']<n,'edit_index_type_or_bounds')
    expected=[i for i in range(n) if i!=deleted]
    need(origins==expected and all(reverse[i]==j for j,i in enumerate(expected)),'map_order')

def require_equal_rows(a,b,clock,role):
    need(a==b,'aligned_row_mismatch',clock=clock,role=role)

def require_same_observations(original,candidate):
    need(original['owned_stream']==candidate['owned_stream'],'owned_stream_changed')
    need(original['clears']==candidate['clears'],'clear_mismatch')
    need(original['interfaces']==candidate['interfaces'],'owned_interface_mismatch')
    need(original['copy_guards']==candidate['copy_guards'],'copy_guard_mismatch')

def require_observation_inventory(replay,program,reverse,public):
    expected={'clears':[],'interfaces':[],'copy_guards':[],'owned_stream':[]}
    for i,e in enumerate(program):
        op=e[0];r=e[1]
        if op=='CLEAR':expected['clears'].append(i)
        if op=='COPY':expected['copy_guards'].append(i)
        if op in ('ADD','COPY','SCALE') and (r>=public or (op!='SCALE' and e[2]>=public)):expected['interfaces'].append(i)
        if op in ('INIT','CLEAR') or (op=='MOVE' and r>=public):expected['owned_stream'].append(i)
    counts={'clears':204,'interfaces':700,'copy_guards':1,'owned_stream':455}
    for name,clocks in expected.items():
        need(len(clocks)==counts[name],'source_inventory_count',name=name,actual=len(clocks))
        observed=replay[name];need(isinstance(observed,list) and len(observed)==counts[name],'observation_count',name=name)
        for item,clock in zip(observed,clocks):
            need(isinstance(item,dict) and type(item.get('original_clock')) is int and item['original_clock']==clock,'observation_origin',name=name,clock=clock)
            c=item.get('candidate_clock');need(type(c) is int and 0<=c<len(program)-1 and type(reverse[clock]) is int and c==reverse[clock],'observation_candidate_clock',name=name,clock=clock)
    return counts

def final_public_nonidentity(rows,mains,n):
    need(len(rows)>=n and mains and all(type(r) is int and 0<=r<n for r in mains),'public_final_inventory')
    count=sum(rows[r]!={str(r):'1'} for r in mains)
    need(count>0,'public_final_identity')
    for r in range(n):
        if r not in mains:need(rows[r]=={str(r):'1'},'helper_not_identity',role=r)
    return count

def run(root,built):
    op=root/'inputs/pr7624/research/p104-w2-primal-dual-bypass/data/word.json.gz';bp=built/'candidate-word.json.gz';mp=built/'edit-manifest.json'
    raw=op.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    need(sha(raw)==SOURCE_GZ and blob==SOURCE_BLOB,'source_custody')
    old=load(op);new=load(bp);manifest=load(mp);status=load(built/'status.json')
    need(sha(canon(old))==SOURCE_CAN,'source_canonical_hash');need(status['status']=='CANDIDATE_BUILT_UNQUALIFIED','builder_status')
    csha=sha(canon(new));gzsha=sha(bp.read_bytes());meta=sha(canon({k:v for k,v in old.items() if k!='program'}))
    need(manifest['schema']=='compose7624-edit-manifest/v1' and manifest['source_canonical_sha256']==SOURCE_CAN and manifest['source_gzip_sha256']==SOURCE_GZ and manifest['source_git_blob']==SOURCE_BLOB and manifest['candidate_canonical_sha256']==status['candidate_canonical_sha256']==csha and manifest['candidate_gzip_sha256']==status['candidate_gzip_sha256']==gzsha and manifest['metadata_sha256']==meta,'manifest_hash_binding')
    def operands(e):
        need(isinstance(e,list) and len(e)>=2,'incident_event_shape')
        if e[0] in ('ADD','COPY'):
            need(len(e)==5,'incident_scalar_shape');return {e[1],e[2]}
        need(e[0] in ('MOVE','SCALE','INIT','CLEAR'),'incident_opcode');return {e[1]}
    incidents=[(i,old['program'][i]) for i in range(WINDOW[0],WINDOW[1]+1) if operands(old['program'][i]) & {902,1091}]
    need(incidents==INCIDENTS,'incident_window_mismatch')
    need(manifest['incident_window']=={'inclusive':list(WINDOW),'roles':[902,1091],'events':[[i,e] for i,e in INCIDENTS]},'manifest_incident_mismatch')
    need(len(old['program'])==77372 and len(new['program'])==77371,'event_count')
    need({k:v for k,v in old.items() if k!='program'}=={k:v for k,v in new.items() if k!='program'},'metadata_changed')
    validate_maps(manifest,len(old['program']),38623)
    origins=[];rebuilt=[];reverse=[None]*len(old['program'])
    for i,event in enumerate(old['program']):
        e=event
        if i in PATCH:
            before,after=PATCH[i];need(e==before,'literal_patch_mismatch',origin=i)
            if after is None:continue
            e=after
        reverse[i]=len(rebuilt);origins.append(i);rebuilt.append(e)
    need(new['program']==rebuilt,'independent_reconstruction_mismatch')
    need(manifest['candidate_origins']==origins and manifest['original_to_candidate']==reverse,'origin_map_mismatch')
    need(manifest['edits']==[{'original_index':i,'old':x,'new_or_null':y} for i,(x,y) in PATCH.items()],'manifest_edits_mismatch')
    need(reverse[38623] is None and all(reverse[i]==(i if i<38623 else i-1) for i in range(len(reverse)) if i!=38623),'clock_map')
    # Compare the actual complete non-MOVE stream; only the public contact chart changes.
    a=[(i,x) for i,x in enumerate(old['program']) if x[0]!='MOVE']
    b=[(origins[j],x) for j,x in enumerate(new['program']) if x[0]!='MOVE']
    need(len(a)==len(b),'scalar_stream_length')
    for (i,x),(k,y) in zip(a,b):
        need(i==k,'scalar_origin_mismatch',clock=i)
        if i==40279:need(x==PATCH[i][0] and y==PATCH[i][1] and x[:4]==y[:4],'contact_scalar_mismatch',clock=i)
        else:need(x==y,'nonmove_stream_mismatch',clock=i)
    oldr=Replay(old,list(range(len(old['program']))),reverse,'original')
    newr=Replay(new,origins,reverse,'candidate')
    need(oldr.rows==newr.rows and oldr.alive==newr.alive,'initial_state_mismatch')
    # Every operation changes at most its destination row. Compare that row after
    # each aligned operation, and the two source rows before each scalar. The
    # unchanged rows retain the initial equality by induction. The one deleted
    # public MOVE is a normalized-row identity slot.
    steps=0;scalar_steps=0
    for i,x in enumerate(old['program']):
        j=reverse[i]
        if j is None:
            need(i==38623 and x==PATCH[i][0] and x[0]=='MOVE','invalid_virtual_slot',clock=i)
            oldr.step(i,x)
            need(oldr.rows[x[1]]==newr.rows[x[1]] and oldr.alive==newr.alive,'deleted_move_row_mismatch',clock=i)
            steps+=1;continue
        y=new['program'][j];need(origins[j]==i,'alignment',clock=i)
        need(x[0]==y[0] and x[1]==y[1],'aligned_destination_mismatch',clock=i)
        r=x[1]
        require_equal_rows(oldr.rows[r],newr.rows[r],i,r)
        if x[0] in ('ADD','COPY'):
            need(x[2]==y[2] and x[3]==y[3] and oldr.rows[x[2]]==newr.rows[y[2]],'source_before_mismatch',clock=i)
        oldr.step(i,x);newr.step(j,y)
        require_equal_rows(oldr.rows[r],newr.rows[r],i,r)
        need(oldr.alive==newr.alive and oldr.occ==newr.occ,'aligned_state_mismatch',clock=i,role=r)
        if x[0] in ('ADD','COPY','SCALE'):
            need(oldr.lit.result()==newr.lit.result() and oldr.trajectory.result()==newr.trajectory.result(),'aligned_grid_mismatch',clock=i)
            scalar_steps+=1
        steps+=1
    need(oldr.rows==newr.rows,'all_final_rows_mismatch')
    original=oldr.finish();candidate=newr.finish();candidate['virtual_deleted_interfaces']=[]
    need(original['endpoint_rows']==candidate['endpoint_rows'] and original['end_charts']==candidate['end_charts'],'endpoint_mismatch')
    live=set(old['live']);mains=live|{x+112 for x in live}|set(old['hosted']['X2'])|set(old['hosted']['Y2'])
    nonidentity=final_public_nonidentity(original['endpoint_rows'],mains,1501)
    need(final_public_nonidentity(candidate['endpoint_rows'],mains,1501)==nonidentity,'public_nonidentity_count_changed')
    inventories=require_observation_inventory(original,old['program'],reverse,1501)
    need(require_observation_inventory(candidate,old['program'],reverse,1501)==inventories,'candidate_inventory_changed')
    require_same_observations(original,candidate)
    need(original['owned_stream']==candidate['owned_stream'],'owned_stream_changed')
    need(original['owned_labels']==candidate['owned_labels'],'used_owned_label_set_changed')
    need(original['clears']==candidate['clears'] and len(original['clears'])==204,'clear_mismatch')
    need(original['interfaces']==candidate['interfaces'],'owned_interface_mismatch')
    need(original['copy_guards']==candidate['copy_guards'],'copy_guard_mismatch')
    need(original['grid']==candidate['grid'],'grid_mismatch')
    oroutes=original['routes'];nroutes=candidate['routes'];changed_routes=sorted(int(k) for k in set(oroutes)|set(nroutes) if oroutes.get(k,[])!=nroutes.get(k,[]))
    need(changed_routes==[902,1091],'unexpected_changed_routes',roles=changed_routes)
    for mode in ('literal','trajectory'):
        o=original['grid'][mode];n=candidate['grid'][mode]
        need(n['max_den_exp']==o['max_den_exp']<=25 and n['odd_den_lcm']==o['odd_den_lcm'] and o['odd_den_lcm'] and 1125%o['odd_den_lcm']==0 and n['max_num_bits']==o['max_num_bits'],'grid_increase',mode=mode,original=o,candidate=n)
    source_grid_contract(original,candidate)
    oc=census(old,original);nc=census(new,candidate)
    dp=difference(oc['native_paid'],nc['native_paid']);dt=difference(oc['native_targets'],nc['native_targets'])
    need(dp=={'1':-2,'2':2,'3':-1,'4':-1,'5':1} and dt=={} and oc['owned_moves']==nc['owned_moves'] and oc['owned_rises']==nc['owned_rises'],'census_mismatch',delta_p=dp,delta_t=dt)
    need(oc['lifetimes']==nc['lifetimes']==204 and oc['peak']==nc['peak']==50,'lifecycle_census_mismatch')
    changes={'clears':[],'interfaces':[],'copy_guards':[]}
    return {'schema':'compose7624-exact/v1','scope':'Conditional on common U; 1569 dirty entry symbols, literal INIT and CLEAR reset full extent; not a physical, erasure-service, or price qualification.',
      'source':{'original_canonical_sha256':SOURCE_CAN,'original_gzip_sha256':SOURCE_GZ,'candidate_canonical_sha256':csha,'candidate_gzip_sha256':gzsha,'manifest_sha256':sha(mp.read_bytes())},
      'original':original,'candidate':candidate,'changed':changes,'alignment':{'source_steps':steps,'scalar_steps':scalar_steps,'deleted_identity_clock':38623,'all_rows_equal_by_destination_induction':True,'normalized_nonmove_stream_equal':True,'observation_inventory':inventories,'public_final_nonidentity_count':nonidentity},
      'census':{'original':oc,'candidate':nc,'native_delta_p':dp,'native_delta_t':dt,'seventeen_delta_p':{k:17*v for k,v in dp.items()}}}

def controls():
    results=[]
    def reject(name,fn,reason):
        try:fn()
        except Refusal as e:
            need(e.reason==reason,'control_wrong_rejection',control=name,actual=e.reason,expected=reason)
            results.append(name);return
        raise Refusal('control_did_not_reject',control=name)
    w={'public':1501,'owned_fields':68,'frames':[[],[1]],'initial':[0]*1501,'final':[0]*1501}
    def fresh():return Replay(w,list(range(12)),list(range(12)),'control')
    r=fresh();need(r.rows[1501]=={1501:F(1)},'control_dirty_entry')
    r.step(0,['INIT',1501,0]);need(r.rows[1501]=={},'control_init_not_zero')
    r.step(1,['COPY',1501,0,'2',0]);need(r.rows[1501]=={0:F(2)} and len(r.guards)==1,'control_copy_assignment')
    before=(r.rows[1501].copy(),r.lit.result(),r.trajectory.result(),list(r.guards),list(r.interfaces))
    reject('dirty_copy_before_write',lambda:r.step(2,['COPY',1501,0,'-2',0]),'copy_nonzero')
    need(before==(r.rows[1501],r.lit.result(),r.trajectory.result(),r.guards,r.interfaces),'dirty_copy_mutated_state')
    r.step(3,['CLEAR',1501,0]);need(r.rows[1501]=={} and 1501 not in r.alive,'control_clear')
    z=fresh()
    reject('inactive_owned_read',lambda:z.step(0,['ADD',0,1501,'1',0]),'owned_not_live')
    reject('negative_operand',lambda:z.step(0,['ADD',0,-1,'1',0]),'bad_operand')
    reject('unknown_opcode',lambda:z.step(0,['UNKNOWN',0]),'unknown_event')
    reject('coframe',lambda:z.step(0,['ADD',0,1,'1',1]),'scalar_coframe_or_zero')
    reject('nonstrict_move',lambda:z.step(0,['MOVE',0,0,0,False]),'move_not_strict_nested')
    good={'candidate_origins':[0,2,3],'original_to_candidate':[0,None,1,2],'edits':[{'original_index':1}]}
    validate_maps(good,4,1)
    for name,bad in [('boolean_origin',{'candidate_origins':[False,2,3],'original_to_candidate':[0,None,1,2],'edits':[{'original_index':1}]}),('negative_origin',{'candidate_origins':[-1,2,3],'original_to_candidate':[0,None,1,2],'edits':[{'original_index':1}]}),('boolean_reverse',{'candidate_origins':[0,2,3],'original_to_candidate':[False,None,1,2],'edits':[{'original_index':1}]}),('boolean_edit',{'candidate_origins':[0,2,3],'original_to_candidate':[0,None,1,2],'edits':[{'original_index':True}]})]:
        expected='edit_index_type_or_bounds' if name=='boolean_edit' else ('reverse_type_or_bounds' if name=='boolean_reverse' else 'origin_type_or_bounds')
        reject(name,lambda bad=bad:validate_maps(bad,4,1),expected)
    require_equal_rows({0:F(1)},{0:F(1)},1,0)
    reject('changed_normalized_row',lambda:require_equal_rows({0:F(1)},{0:F(2)},1,0),'aligned_row_mismatch')
    # Source-free inventory fixture exercises the same non-vacuity and clock
    # checks used for actual source-derived observation keys.
    program=([['CLEAR',1501,0]]*204 + [['INIT',1501,0]]*251 +
             [['ADD',1501,0,'1',0]]*700 + [['COPY',0,1,'1',0]] + [['MOVE',0,0,1,False]])
    reverse=list(range(len(program)-1))+[None]
    inv={'clears':[],'interfaces':[],'copy_guards':[],'owned_stream':[]}
    for i,event in enumerate(program):
        op=event[0];record={'original_clock':i,'candidate_clock':i}
        if op=='CLEAR':inv['clears'].append(dict(record))
        if op in ('CLEAR','INIT'):inv['owned_stream'].append(dict(record))
        if op=='ADD':inv['interfaces'].append(dict(record))
        if op=='COPY':inv['copy_guards'].append(dict(record))
    require_observation_inventory(inv,program,reverse,1501)
    empty={k:[] for k in inv}
    reject('empty_observations',lambda:require_observation_inventory(empty,program,reverse,1501),'observation_count')
    reject('empty_source_inventory',lambda:require_observation_inventory(empty,[],[],1501),'source_inventory_count')
    missing={k:list(v) for k,v in inv.items()};missing['interfaces']=missing['interfaces'][:-1]
    reject('missing_observation',lambda:require_observation_inventory(missing,program,reverse,1501),'observation_count')
    duplicate={k:list(v) for k,v in inv.items()};duplicate['interfaces'][1]=dict(duplicate['interfaces'][0])
    reject('duplicate_observation',lambda:require_observation_inventory(duplicate,program,reverse,1501),'observation_origin')
    badclock={k:list(v) for k,v in inv.items()};badclock['clears'][0]=dict(badclock['clears'][0],candidate_clock=False)
    reject('boolean_observation_clock',lambda:require_observation_inventory(badclock,program,reverse,1501),'observation_candidate_clock')
    negclock={k:list(v) for k,v in inv.items()};negclock['clears'][0]=dict(negclock['clears'][0],candidate_clock=-1)
    reject('negative_observation_clock',lambda:require_observation_inventory(negclock,program,reverse,1501),'observation_candidate_clock')
    fixture={'owned_stream':[{'x':1}],'clears':[{'row':{'0':'1'}}],'interfaces':[{'x':2}],'copy_guards':[{'x':3}]}
    require_same_observations(fixture,fixture)
    bad={k:list(v) for k,v in fixture.items()};bad['clears']=[{'row':{'0':'2'}}]
    reject('changed_clear',lambda:require_same_observations(fixture,bad),'clear_mismatch')
    bad2={k:list(v) for k,v in fixture.items()};bad2['interfaces']=[{'x':99}]
    reject('changed_owned_interface',lambda:require_same_observations(fixture,bad2),'owned_interface_mismatch')
    public=[{'0':'1'},{'1':'1'}]
    reject('full_rank_identity_endpoint',lambda:final_public_nonidentity(public,{0,1},2),'public_final_identity')
    need(final_public_nonidentity([{'0':'1','1':'1'},{'1':'1'}],{0,1},2)==1,'control_nonidentity')
    return {'status':'PASS_SOURCE_FREE_CONTROLS','rejected':results,'positive':['dirty_init_zero','clean_copy_assignment','clear','changed_public_operator']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path);p.add_argument('--built',type=Path);p.add_argument('--out',type=Path);p.add_argument('--controls-only',action='store_true');a=p.parse_args()
    if a.controls_only:
        try:print(json.dumps(controls(),sort_keys=True));return 0
        except Exception as e:print(json.dumps({'status':'REFUSED','reason':getattr(e,'reason',type(e).__name__),'detail':getattr(e,'detail',str(e))},sort_keys=True));return 1
    if a.root is None or a.built is None or a.out is None:p.error('--root, --built and --out are required unless --controls-only is set')
    a.out.mkdir(parents=True,exist_ok=False)
    try:
        result=run(a.root,a.built);raw=canon(result)
        with (a.out/'EXACT.json.gz').open('wb') as f:
            with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:z.write(raw)
        status={'status':'U_CONDITIONAL_LITERAL_EXACT_ONLY','exact_sha256':sha(raw),'exact_gzip_sha256':sha((a.out/'EXACT.json.gz').read_bytes()),'source':result['source'],'changed_clear_count':len(result['changed']['clears']),'changed_interface_count':len(result['changed']['interfaces']),'limits':result['scope']};code=0
    except Refusal as e:status={'status':'REFUSED','reason':e.reason,'detail':e.detail};code=1
    except Exception as e:status={'status':'REFUSED','reason':'unexpected_exception','type':type(e).__name__,'detail':str(e)};code=1
    (a.out/'status.json').write_text(json.dumps(status,sort_keys=True,indent=2)+'\n');return code
if __name__=='__main__':raise SystemExit(main())
