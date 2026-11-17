#!/usr/bin/env python3
"""Independent exact strict-74 source/candidate review; no physical replay."""
import collections,datetime,gzip,hashlib,importlib.util,json,os,resource,signal,sys,time
from fractions import Fraction as Q
from pathlib import Path
from exact import Interpreter, Reject, diff
D=Path(__file__).resolve().parent;P=D.parent/'port74';S=P/'source7644'
PIN={
 'base':(S/'data/word.json.gz','1b0efdc59fe3f8056f3dbfdd618c7f5b4b4f0ed4063689f182ae3dbd1138fede','86bc8a1d1276c5b8d80a19704f90279e85b24b9490a02b9afa67c1a5b119c114'),
 'child':(P/'candidate.json.gz','f4e8d0c000ee3f2a1bd51e5c52715c7aef40946f768c5f19c101bce4f1ae1448','6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf'),
 'peer':(S/'data/peer7611.json','64f096802f328cac7e51c655c2c5a1aa6c011dd33ea278c53a05caaa598594df',None),
 'base_invoice':(S/'data/invoice.json','5ea13a376c00be2363e9508f23d9ceaf299fb297fb54c82a6cd2b8559aa92bac',None),
 'child_invoice':(P/'candidate-invoice.json','7d54c1ec036d4c096526dd95e06892ca99210812d51a503b22f6d78243330ca9',None),
 'price_engine':(S/'independent.py','b657117ba89a85b0cf2459236e0f117cff1c4c46b208449b2484c415e3136a3d',None)}
REMOVED={43543:['MOVE',46,513,914,False],43544:['ADD',145,46,'1',914],45387:['MOVE',46,914,245,False],45388:['ADD',1456,46,'1',245],45390:['ADD',588,46,'-1',245],47973:['MOVE',46,245,127,False]}
INSERT={43543:[['ADD',145,818,'-1',914]],45392:[['ADD',588,818,'1',245],['ADD',1456,818,'-1',245]],47973:[['MOVE',46,513,127,False]]}
def need(x,m):
 if not x:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def unique(x):
 d={}
 for k,v in x:need(k not in d,'duplicate JSON key');d[k]=v
 return d
def load(name):
 path,pin,raw=PIN[name];b=path.read_bytes();need(sha(b)==pin,'pin '+name)
 if raw:b=gzip.decompress(b);need(sha(b)==raw,'raw '+name)
 return json.loads(b,object_pairs_hook=unique)
def roles(e):return e[1:3] if e[0] in ('ADD','COPY') else e[1:2]
def map_origins(a,b,peer):
 need({k:v for k,v in a.items() if k!='program'}=={k:v for k,v in b.items() if k!='program'},'header')
 ap,bp=a['program'],b['program'];edits=dict(peer['insert_before']);prefix=[e for e in edits[0] if e[1] not in (185,196)]
 need(len(prefix)==24 and bp[:24]==prefix,'24 source-pinned entrance operations')
 need(all(ap[i]==e for i,e in REMOVED.items()),'literal removed anchors')
 need(ap[45391]==['MOVE',818,914,245,False] and ap[45392]==['ADD',818,1456,'1',245],'818 anchors')
 need(edits[43525]==INSERT[43543] and edits[45372]==INSERT[45392] and edits[47953]==INSERT[47973],'pinned donor edits')
 j=24;origin={};insert_indices=[]
 for i,e in enumerate(ap):
  for ins in INSERT.get(i,[]):
   need(bp[j]==ins,'insert anchor '+str(i));insert_indices.append(j);j+=1
  if i not in REMOVED:
   need(bp[j]==e,'mapped origin '+str(i));origin[i]=j;j+=1
 need(j==len(bp),'candidate trailing events');return origin,insert_indices
def observe(interpreter,rr):return interpreter.snapshot(sorted(set(rr)))
def compare_snapshot(x,y,clock,phase):
 for role in x:
  u,v=x[role],y[role]
  if u[0]!=v[0] or u[1]!=v[1] or u[2]!=v[2]:
   raise ValueError('observation %s source=%s role=%s charts=%s/%s difference=%s'%(phase,clock,role,u[1],v[1],diff(v[2],u[2])))
def replay_base(w,origin):
 a=Interpreter(w);n=w['public'];observations={};clear_count=copy_count=0
 for i,e in enumerate(w['program']):
  rr=roles(e);watch=any(r>=n for r in rr) or e[0]=='COPY'
  if watch:
   need(i in origin,'missing private/COPY origin '+str(i));before=observe(a,rr)
  if e[0]=='CLEAR':clear_count+=1
  if e[0]=='COPY':copy_count+=1
  a.step(i)
  if watch:observations[origin[i]]=(i,rr,before,observe(a,rr))
 a.end();need(clear_count==74,'74 baseline CLEARs');return a,observations,copy_count
def replay_child(w,observations,baseline,mutant=False):
 a=Interpreter(w);checked=0
 for j,e in enumerate(w['program']):
  if j in observations:
   i,rr,before,after=observations[j]
   try:compare_snapshot(before,observe(a,rr),i,'before')
   except ValueError as x:
    if mutant:return {'rejected':True,'first_witness':str(x)}
    raise
  try:a.step(j)
  except Reject as x:
   if mutant:return {'rejected':True,'first_witness':str(x)}
   raise
  if j in observations:
   try:compare_snapshot(after,observe(a,rr),i,'after')
   except ValueError as x:
    if mutant:return {'rejected':True,'first_witness':str(x)}
    raise
   checked+=1
 a.end()
 for r in range(a.n):
  if baseline.rows[r]!=a.rows[r]:
   if mutant:return {'rejected':True,'first_witness':{'output_role':r,'difference':diff(a.rows[r],baseline.rows[r])}}
   raise ValueError('final row '+str(r)+' '+str(diff(a.rows[r],baseline.rows[r])))
 if mutant:return {'rejected':False}
 need(all(not r for r in a.rows[a.n:]),'nonempty final owned row')
 return a,checked
def census(w):
 n=w['public'];dim=list(map(len,w['frames']));main=set(w['live']);main|={r+112 for r in w['live']};main|=set(w['hosted']['X2'])|set(w['hosted']['Y2'])
 return (collections.Counter(abs(dim[e[3]]-dim[e[2]]) for e in w['program'] if e[0]=='MOVE'),collections.Counter(dim[w['final'][r]]-dim[w['initial'][r]] for r in range(n) if r not in main))
def fmt(c):return {str(k):v for k,v in sorted(c.items()) if v}
def delta(a,b):
 x=collections.Counter(b);x.subtract(a);return fmt(x)
def controls():
 a=Interpreter({'public':1,'owned_fields':1,'frames':[[],[1]],'initial':[0],'final':[1],'program':[['MOVE',0,1,0,False]]})
 try:a.step(0)
 except Reject:pass
 else:raise AssertionError('wrong route accepted')
 try:compare_snapshot({0:(True,0,{0:Q(1)})},{0:(True,0,{0:Q(2)})},0,'fixture')
 except ValueError:pass
 else:raise AssertionError('corrupted private observer accepted')
 print('PASS_CONTROLS: wrong MOVE route and changed observed public row reject')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 if sys.argv[1:]==['--fixtures']:controls();return
 if len(sys.argv)!=4 or sys.argv[1]!='--execute' or sys.argv[2]!='--freeze-sha256' or not __debug__:raise SystemExit('explicit --execute --freeze-sha256 <hash> required')
 os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,)*2);resource.setrlimit(resource.RLIMIT_CPU,(570,570));signal.alarm(600)
 freeze=D/'FREEZE.json';need(sha(freeze.read_bytes())==sys.argv[3],'freeze hash')
 for x in json.loads(freeze.read_text())['files']:need(sha(Path(x['path']).read_bytes())==x['sha256'],'freeze dependency')
 started=now();tick=time.monotonic()
 with (D/'RESULT.json').open('x') as out:
  try:
   base=load('base');child=load('child');peer=load('peer');bi=load('base_invoice');ci=load('child_invoice')
   need((base['public'],base['owned_fields'])==(1501,68),'source dimensions')
   origin,insert_indices=map_origins(base,child,peer);baseline,obs,copies=replay_base(base,origin);candidate,checked=replay_child(child,obs,baseline)
   need(len(baseline.lifetimes)==len(candidate.lifetimes)==74 and baseline.peak==candidate.peak,'lifetime/peak')
   # Corrupt an actual added correction, not merely a synthetic linear operator.
   altered=dict(child);altered['program']=list(child['program']);j=insert_indices[0];bad=list(altered['program'][j]);need(bad==['ADD',145,818,'-1',914],'mutation anchor');bad[3]='1';altered['program'][j]=bad
   mutation=replay_child(altered,obs,baseline,True);need(mutation['rejected'],'mutated correction accepted')
   bp,bt=census(base);cp,ct=census(child);need(bt==ct,'native target changed')
   oldp=collections.Counter({int(k):v for k,v in bi['paid'].items()});oldt=collections.Counter({int(k):v for k,v in bi['targets'].items()})
   residualp=oldp.copy();residualp.subtract({k:17*v for k,v in bp.items()});residualt=oldt.copy();residualt.subtract({k:17*v for k,v in bt.items()})
   need(all(v>=0 for v in residualp.values()) and all(v>=0 for v in residualt.values()),'negative caller residual')
   newp=collections.Counter({k:17*v for k,v in cp.items()});newp.update(residualp);newt=collections.Counter({k:17*v for k,v in ct.items()});newt.update(residualt)
   need(fmt(newp)==ci['paid'] and fmt(newt)==ci['targets'],'actual candidate invoice mismatch')
   pp,ph,_=PIN['price_engine'];need(sha(pp.read_bytes())==ph,'price engine pin');spec=importlib.util.spec_from_file_location('retained_7644_price',pp);engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
   hist=lambda p,t:{k:t.get(k,0)-p.get(k,0) for k in p.keys()|t.keys()};ob=engine.crossing(hist(oldp,oldt));nb=engine.crossing(hist(newp,newt));need(nb[0]>ob[1],'no strict directed price gain');need(not ob[0]>nb[1],'reversed price control')
   result={'status':'PASS_INDEPENDENT_STRICT74','started_utc':started,'ended_utc':now(),'elapsed_seconds':time.monotonic()-tick,
     'base_head':'32cfa1d20d3e4587dc601e69ccac1cd24a239e5c','base_word':PIN['base'][2],'candidate_word':PIN['child'][2],
     'arbitrary_public_inputs':1501,'matched_public_outputs':1501,'equal_terminal_owned_zero_rows':68,
     'old_private_or_copy_events_compared_before_after':checked,'source_copy_count':copies,'ordered_original_clears':74,
     'source_peak':baseline.peak,'candidate_peak':candidate.peak,
     'native_paid_delta':delta(bp,cp),'native_target_delta':delta(bt,ct),'signed17_paid_delta':delta(oldp,newp),'signed17_target_delta':delta(oldt,newt),
     'source_raw_bracket':[str(v) for v in ob],'candidate_raw_bracket':[str(v) for v in nb],'strict_lower_gain':str(nb[0]-ob[1]),
     'source_free_controls':'wrong route and altered public observer rejected','actual_correction_mutation':mutation,'reversed_price_rejected':True,
     'price_provenance':'retained pinned #7644 decimal directed and dyadic integer-root engine; not independently authored in this checker',
     'scope':'exact rational public rows and retained private/COPY observations; 17-call invoice residual arithmetic; no fresh full signed/native application, physical covariance, common-U or rounded reset'}
  except BaseException as e:
   result={'status':'FAILED_OR_INTERRUPTED','started_utc':started,'ended_utc':now(),'elapsed_seconds':time.monotonic()-tick,'error_type':type(e).__name__,'error':str(e),'automatic_retry':False}
   json.dump(result,out,indent=2,sort_keys=True);out.write('\n');out.flush();raise
  json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
 print(json.dumps({'status':result['status'],'started_utc':started,'ended_utc':result['ended_utc'],'elapsed_seconds':result['elapsed_seconds']}))
if __name__=='__main__':main()
