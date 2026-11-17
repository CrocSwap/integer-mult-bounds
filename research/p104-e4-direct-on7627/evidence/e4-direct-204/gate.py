#!/usr/bin/env python3
"""Fixed E4 exact gate. One invocation only after independent review and GO."""
import collections, gzip, hashlib, json, os, resource, signal, sys, time, tempfile
from fractions import Fraction as Q
from pathlib import Path
import reviewed_oracle as o

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
WORD=ROOT/'outputs/kappa-swarm30-20261116/agents/joint/candidate-word.json.gz'
CERT=ROOT/'outputs/kappa-target368-20261116/agents/owned1532-early-595/candidate-certificates.json'
GZ='3b0947df9d291308279a00e009f9c1f845151b5b40f81960a53a2949cb44c9a9'
CAN='b80b6e74bff87c8d8160c5e121dac7c68df0827a7061847b896075417a346238'
CERT_SHA='6df3d99cf8074412dab9035c593f657a8b449c80a49b7b4a5fbb99ce3d8a956a'
ANCHORS={41629:['MOVE',490,594,725,False],41631:['ADD',490,296,'1',725],43041:['MOVE',490,725,883,False],45133:['CLEAR',1531,541],49462:['MOVE',1394,165,127,False],50991:['MOVE',538,883,127,False],54324:['MOVE',1427,176,127,False]}
CUTS={49462:(1394,Q(-1),2),50991:(538,Q(-1),2),54324:(1427,Q(1,2),17)}
def need(v,m):
 if not v: raise o.Refusal(m)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def addrow(dst,src,q):
 out=dst.copy()
 for k,v in src.items():
  z=out.get(k,Q(0))+q*v
  if z: out[k]=z
  else: out.pop(k,None)
 return out
def coefficients(word):
 """Inverse coordinates of S on the live public chart-127 bank."""
 cur=list(word['initial']); lam={}; out={}
 for i,e in enumerate(word['program']):
  op,r=e[:2]
  if op=='MOVE' and r<o.PUBLIC:
   need(cur[r]==e[2],'public chart chronology');cur[r]=e[3]
   if lam and e[2]==127 and e[3]!=127: need(not lam.get(r),'nonzero provider leaves 127')
  if lam and op in ('ADD','SCALE','COPY') and e[-1]==127:
   need(r<o.PUBLIC and (op=='SCALE' or e[2]<o.PUBLIC),'owned contact at 127 during decoder')
   if op=='COPY': raise o.Refusal('copy during decoder')
   if op=='SCALE':
    if r in lam: lam[r]/=Q(e[2])
   else:
    s=e[2];lam[s]=lam.get(s,Q(0))-Q(e[3])*lam.get(r,Q(0))
    if not lam[s]: del lam[s]
  if i==49462: lam={268:Q(1),264:Q(1,2)}
  if i in CUTS:
   target,scale,count=CUTS[i]; need(cur[target]==127 and all(cur[x]==127 and x<o.PUBLIC for x in lam),'repair chart and provider')
   need(not lam.get(target),'repair target has nonzero decoder coefficient')
   need(len(lam)==count,'decoder support at '+str(i))
   out[i]=[[ 'ADD',target,s,str(scale*q),127] for s,q in sorted(lam.items()) if q]
   if i==54324: break
 return out

def project(word, corrections, mutation=None):
 p=word['program']; out=[];orig=[]
 for i,e in enumerate(p):
  if i==41629: e=['MOVE',490,594,883,False]
  elif i==41631: e=['ADD',1427,296,'1' if mutation=='wrong_sign' else '-1',725]
  elif i==43041: continue
  out.append(e);orig.append(i)
  if i in corrections:
   es=corrections[i]
   if mutation=='missing_repair' and i==50991: es=[]
   out.extend(es);orig.extend([None]*len(es))
 w=dict(word);w['program']=out
 return w,orig

def certrow(c): return {int(k):Q(v) for k,v in c.items() if Q(v)}
def evaluate(rows, coeff):
 result={}
 for r,q in coeff.items(): result=addrow(result,rows[r],q)
 return result
class Checked(o.Replay):
 def __init__(self,w,orig,certs,reference=None,candidate=False,bad_cert=False, payload=None, corrections=None):
  super().__init__(w,orig,reference);self.certs={x['event']:x for x in certs};self.candidate=candidate;self.bad_cert=bad_cert;self.checked=0;self.s=None;self.identity=False;self.witness=None;self.payload=payload;self.corrections=corrections
 def step(self,j,e):
  i=self.origins[j]
  if i==41631 and not self.candidate: self.s=self.rows[296].copy()
  if i==45133:
   c=self.certs[i];old=certrow(c['certificate']);new=old.copy();new[296]=new.get(296,Q(0))-1;new[570]=new.get(570,Q(0))-Q(1,2);new={r:q for r,q in new.items() if q}
   need(self.cur[296]==861 and self.cur[570]==861,'witness provider charts')
   if self.candidate:
    need(evaluate(self.rows,old)!=self.rows[1531],'old witness unexpectedly succeeds')
    if self.bad_cert: new[296]+=1
    need(evaluate(self.rows,new)==self.rows[1531],'repaired witness fails');self.witness={'old_rejected':True,'new_support':len(new)}
  if e[0]=='CLEAR' and i is not None:
   c=self.certs.get(i);need(c is not None and c['field']==e[1] and c['chart']==e[2] and c['verified_exact'] is True,'certificate metadata')
   want=certrow(c['erased']);need(self.rows[e[1]]==want,'erased row differs')
   co=certrow(c['certificate'])
   need(all(0<=r<o.PUBLIC and self.cur[r] is not None for r in co),'certificate provider live public')
   if self.candidate and i==45133:
    co[296]=co.get(296,Q(0))-1;co[570]=co.get(570,Q(0))-Q(1,2);co={r:q for r,q in co.items() if q}
   need(evaluate(self.rows,co)==want,'certificate equation')
   self.checked+=1
  super().step(j,e)
  if self.candidate and i in CUTS:
   scale=CUTS[i][1]; co={e[2]:Q(e[3])/scale for e in self.corrections[i]}; need(evaluate(self.rows,co)==self.payload,'candidate full S identity at '+str(i))
  if i==49462 and not self.candidate:
   need(self.s is not None and addrow(self.rows[268],self.rows[264],Q(1,2))==self.s,'full S identity');self.identity=True

def compare(w,orig,base,certs,corr,bad=False):
 r=Checked(w,orig,certs,base.obs,True,bad,base.s,corr).run()
 need(r.checked==204 and r.rows==base.rows and r.cur==base.cur,'candidate complete endpoint or certificates')
 return r

def load():
 raw=WORD.read_bytes();need(hashlib.sha256(raw).hexdigest()==GZ and digest(CERT)==CERT_SHA,'input sha');w=json.loads(gzip.decompress(raw));need(o.sha(o.canon(w))==CAN,'canonical sha');need(len(w['program'])==77373,'event census')
 for i,e in ANCHORS.items():need(w['program'][i]==e,'anchor '+str(i))
 c=json.loads(CERT.read_bytes());need(len(c)==204 and len({x['event'] for x in c})==204,'certificate count')
 return w,c

def run():
 need(sys.flags.optimize==0,'optimized Python forbidden')
 o.source_free_controls();w,c=load();corr=coefficients(w);cand,orig=project(w,corr)
 need(len(cand['program'])==77393,'candidate census')
 # Exact structural correspondence positively preserves all original protected events.
 expected=[(i,e) for i,e in enumerate(w['program']) if o.special(e)]
 got=[(orig[j],e) for j,e in enumerate(cand['program']) if o.special(e)]
 need(got==expected,'protected projection mismatch')
 base=Checked(w,list(range(len(w['program']))),c).run();need(base.checked==204 and base.identity,'source certificate/identity')
 mains=set(w['live'])|{x+112 for x in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2']);o.final_public_nonidentity(base.rows,mains)
 result=compare(cand,orig,base,c,corr)
 failures={}
 for kind in ('wrong_sign','missing_repair','bad_cert'):
  mutated,oi=project(w,corr,kind)
  try: compare(mutated,oi,base,c,corr,kind=='bad_cert')
  except (o.Refusal,ValueError,ZeroDivisionError) as exc: failures[kind]=str(exc)
  else: raise o.Refusal('mutation accepted: '+kind)
  need(('repaired witness fails' in failures[kind] if kind=='bad_cert' else ('protected observation mismatch' in failures[kind] or 'endpoint' in failures[kind] or 'certificate' in failures[kind] or 'witness' in failures[kind])),'mutation wrong reason '+kind)
 mapped=remap_certificates(c,w,cand,orig)
 return {'status':'PASS_LITERAL_EXACT_ONLY','candidate_canonical_sha256':o.sha(o.canon(cand)),'events':len(cand['program']),'source_identity_support':len(base.s),'correction_supports':{str(k):len(v) for k,v in corr.items()},'protected':len(base.obs),'counts':dict(result.cnt),'witness':result.witness,'controls':failures,'scope':'Exact conditional gate only; no physical, supplier, invoice, price or kappa admission.'},cand,mapped,orig

def remap_certificates(certs, source, candidate, origins):
 """Validate every mapped source clock and preserve all non-clock certificate fields."""
 need(len(candidate['program'])==len(origins),'origin length')
 reverse={}
 for j,i in enumerate(origins):
  if i is None: continue
  need(type(i) is int and 0<=i<len(source['program']) and i not in reverse,'duplicate or invalid source origin')
  reverse[i]=j
 def mapped_clock(i, literal):
  need(type(i) is int and 0<=i<len(source['program']) and source['program'][i]==literal,'source certificate clock misbind')
  need(i in reverse and candidate['program'][reverse[i]]==literal,'candidate certificate clock misbind')
  return reverse[i]
 mapped=[]
 for old in certs:
  need(type(old['field']) is int and type(old['chart']) is int and type(old['init_chart']) is int,'certificate metadata type')
  need(type(old['certificate']) is dict and type(old['erased']) is dict,'certificate row schema')
  need(len(old['certificate'])==old['terms'] and len(old['erased'])==old['erased_support'],'certificate support schema')
  for field in ('certificate','erased'):
   for k,v in old[field].items():
    need(type(k) is str and k.isdigit() and type(v) is str and Q(v)!=0,'certificate coefficient schema')
  x=json.loads(json.dumps(old));r=old['field']
  x['event']=mapped_clock(old['event'],['CLEAR',r,old['chart']])
  x['init_event']=mapped_clock(old['init_event'],['INIT',r,old['init_chart']])
  moves=old['owned_moves']
  need(type(moves) is list,'owned moves schema'); mapped_moves=[]
  for item in moves:
   need(type(item) is list and len(item)==3 and all(type(v) is int for v in item),'owned move triple schema')
   clock,a,b=item; mapped_moves.append([mapped_clock(clock,['MOVE',r,a,b,True]),a,b])
  x['owned_moves']=mapped_moves
  if old['event']==45133:
   need(r==1531 and old['chart']==541,'1531 witness metadata')
   co=certrow(old['certificate']);co[296]=co.get(296,Q(0))-1;co[570]=co.get(570,Q(0))-Q(1,2)
   x['certificate']={str(r):str(q) for r,q in sorted(co.items()) if q};x['terms']=len(x['certificate'])
  mapped.append(x)
 return mapped

def finalize(directory, cand, mapped, orig):
 """Production writer; refuse overwrites and verify serialized bytes and hashes."""
 data=o.canon(cand);out=directory/'candidate-word.json.gz'
 with out.open('xb') as f:
  with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:z.write(data)
  f.flush();os.fsync(f.fileno())
 need(gzip.decompress(out.read_bytes())==data,'candidate gzip readback')
 receipt={'candidate_gzip_sha256':digest(out),'candidate_canonical_sha256':o.sha(data)}
 for name,value in [('candidate-certificates.json',mapped),('origins.json',orig)]:
  path=directory/name; expected=o.canon(value)+b'\n'
  with path.open('xb') as f:f.write(expected);f.flush();os.fsync(f.fileno())
  need(path.read_bytes()==expected,'finalizer readback '+name);receipt[name+'_sha256']=digest(path)
 return receipt

def finalizer_controls():
 # Only synthetic data: exercise actual remapper and production serializer.
 p=[['NOP',0] for _ in range(45134)];p[0]=['INIT',1531,594];p[1]=['MOVE',1531,594,541,True];p[45133]=['CLEAR',1531,541]
 source={'program':p};candidate={'program':p.copy()};orig=list(range(len(p)))
 common={'field':1531,'chart':541,'init_chart':594,'event':45133,'init_event':0,'certificate':{'5':'1'},'erased':{'2':'1'},'terms':1,'erased_support':1,'owned_moves':[[1,594,541]],'verified_exact':True}
 mapped=remap_certificates([common],source,candidate,orig)
 need(mapped[0]['owned_moves']==[[1,594,541]] and mapped[0]['erased']==common['erased'] and mapped[0]['certificate']=={'5':'1','296':'-1','570':'-1/2'},'owned move or repaired witness control')
 triples=dict(common)
 bad=dict(common);bad['owned_moves']=1
 try: remap_certificates([bad],source,candidate,orig)
 except o.Refusal as ex: need('owned moves schema' in str(ex),'wrong owned moves refusal')
 else: raise o.Refusal('integer owned moves accepted')
 bad=dict(triples);bad['init_event']=1
 try: remap_certificates([bad],source,candidate,orig)
 except o.Refusal as ex: need('source certificate clock misbind' in str(ex),'wrong clock refusal')
 else: raise o.Refusal('clock misbind accepted')
 badcandidate={'program':p.copy()};badcandidate['program'][1]=['MOVE',1531,594,540,True]
 try: remap_certificates([triples],source,badcandidate,orig)
 except o.Refusal as ex: need('candidate certificate clock misbind' in str(ex),'wrong candidate clock refusal')
 else: raise o.Refusal('candidate clock misbind accepted')
 bad=dict(common);bad['erased_support']=2
 try: remap_certificates([bad],source,candidate,orig)
 except o.Refusal as ex: need('support schema' in str(ex),'wrong support refusal')
 else: raise o.Refusal('invalid erased support accepted')
 with tempfile.TemporaryDirectory(prefix='e4-finalizer-control-') as d:
  receipt=finalize(Path(d),candidate,mapped,orig)
  need(receipt['candidate_canonical_sha256']==o.sha(o.canon(candidate)),'canonical hash control')
  try: finalize(Path(d),candidate,mapped,orig)
  except FileExistsError: pass
  else: raise o.Refusal('finalizer overwrite accepted')
 return {'status':'PASS_SOURCE_FREE_FINALIZER_CONTROLS','positive':['owned_move_triples','witness','hash_readback'],'rejected':['integer_owned_moves','source_clock_misbind','candidate_clock_misbind','erased_support','overwrite']}

def main():
 if len(sys.argv)==2 and sys.argv[1]=='--controls-only':
  need(sys.flags.optimize==0,'optimized Python forbidden');print(json.dumps(finalizer_controls(),sort_keys=True));return 0
 need(len(sys.argv)==2 and sys.argv[1]=='--run-once','requires --run-once')
 need(os.environ.get('E4_INDEPENDENT_GO')=='1','independent GO required')
 freeze=json.loads((HERE/'FREEZE.json').read_bytes());expected=freeze['sha256']
 need(digest(HERE/'gate.py')==expected['gate.py'] and digest(HERE/'reviewed_oracle.py')==expected['reviewed_oracle.py'],'frozen code identity')
 need(digest(WORD)==expected['source_gzip'] and digest(CERT)==expected['certificates'],'frozen input identity')
 need(sys.flags.optimize==0,'optimized Python forbidden')
 # Use exclusive creation for both the marker and output; an incomplete run cannot retry.
 marker=HERE/'RUN-01.started';fd=os.open(marker,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(fd,b'started\n');os.fsync(fd);os.close(fd)
 resource.setrlimit(resource.RLIMIT_CPU,(2400,2401));resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_NPROC,(1,1));signal.alarm(3000)
 try:
  finalizer_controls()
  receipt,cand,mapped,orig=run(); receipt.update(finalize(HERE,cand,mapped,orig))
 except BaseException as ex:
  receipt={'status':'REFUSED_OR_INCOMPLETE','error_type':type(ex).__name__,'message':str(ex)}
 path=HERE/'RUN-01.json'
 with path.open('xb') as f:f.write(o.canon(receipt)+b'\n');f.flush();os.fsync(f.fileno())
 print(json.dumps(receipt,sort_keys=True));return 0 if receipt['status']=='PASS_LITERAL_EXACT_ONLY' else 1
if __name__=='__main__': raise SystemExit(main())
