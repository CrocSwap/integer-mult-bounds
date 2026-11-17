#!/usr/bin/env python3
"""Frozen preparation. Actual replay requires independent review and parent GO."""
import copy, gzip, hashlib, importlib.util, json, os, resource, signal
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; HERE=Path(__file__).resolve().parent
BASE=ROOT/'outputs/kappa-target368-20261116/agents/e4-direct-204'
SOURCE=ROOT/'outputs/kappa-swarm30-20261116/agents/joint/candidate-word.json.gz'
SCERT=ROOT/'outputs/kappa-target368-20261116/agents/owned1532-early-595/candidate-certificates.json'
CHECKER=ROOT/'outputs/kappa-research-20261116b/compose7624_completion/certificates.py'
PINS={SOURCE:'3b0947df9d291308279a00e009f9c1f845151b5b40f81960a53a2949cb44c9a9',SCERT:'6df3d99cf8074412dab9035c593f657a8b449c80a49b7b4a5fbb99ce3d8a956a',CHECKER:'10714b5e758ce2bd23432c7824dbcb719b9f81ae2444a32a2eb25d8d284d1411',BASE/'candidate-word.json.gz':'736d475843e2ca53cad8a193ed582926e2659abaec40895a41d55efd4fca532f',BASE/'candidate-certificates.json':'bda1d8b279c5962e579f261349c432fa511e66a7dc592e8a526353857c629c14',BASE/'origins.json':'7fe3af176684321d4776d50b8fe2209db37889f128e65c940e9fb2770ba16ed2',BASE/'RUN-01.json':'0fc0ba9b143e956e41c30e89550b104b0c451b074aa4d35d5a384ecf957ff337',BASE/'PARENT-01.TERMINAL.json':'39cac72f6709dc2f19ba12cb8b5b1aa6cb5d41452d8ee99d9013fca226e509e5'}
def sha(b):return hashlib.sha256(b).hexdigest()
def need(x,m):
 if not x:raise ValueError(m)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
EDITS={41629:(["MOVE",490,594,725,False],["MOVE",490,594,883,False]),41631:(["ADD",490,296,"1",725],["ADD",1427,296,"-1",725])}
DELETED=(43041,["MOVE",490,725,883,False])
INSERTS={49462:[["ADD",1394,264,"-1/2",127],["ADD",1394,268,"-1",127]],50991:[["ADD",538,264,"-1/2",127],["ADD",538,268,"1/2",127]],54324:[["ADD",1427,19,"-1/16",127],["ADD",1427,264,"1/4",127],["ADD",1427,281,"-1/2",127],["ADD",1427,290,"-1/4",127],["ADD",1427,356,"1/4",127],["ADD",1427,372,"3/32",127],["ADD",1427,531,"1/2",127],["ADD",1427,536,"1/8",127],["ADD",1427,538,"1/8",127],["ADD",1427,824,"-1/2",127],["ADD",1427,1008,"-1/2",127],["ADD",1427,1026,"-1/8",127],["ADD",1427,1072,"-3/4",127],["ADD",1427,1122,"-1/4",127],["ADD",1427,1168,"-1/4",127],["ADD",1427,1229,"1/8",127],["ADD",1427,1272,"-1/4",127]]}
CUT_LITERALS={49462:["MOVE",1394,165,127,False],50991:["MOVE",538,883,127,False],54324:["MOVE",1427,176,127,False]}
def bind_origins(source,candidate,orig):
 need(len(source)==77373 and len(candidate)==len(orig)==77393,'word/origin length')
 need([x for x in orig if x is not None]==[i for i in range(len(source)) if i!=DELETED[0]],'origin bijection/order')
 need(source[DELETED[0]]==DELETED[1],'deleted literal')
 for i,(old,new) in EDITS.items():need(source[i]==old,'substitution source literal')
 for i,e in CUT_LITERALS.items():need(source[i]==e,'cut literal')
 expected=[]; eo=[]
 for i,e in enumerate(source):
  if i==DELETED[0]:continue
  expected.append(EDITS[i][1] if i in EDITS else e);eo.append(i)
  if i in INSERTS:
   expected.extend(INSERTS[i]);eo.extend([None]*len(INSERTS[i]))
 need(orig==eo,'insertion location')
 need(candidate==expected,'mapped or inserted event mismatch')
 return True

def origin_controls():
 source=[['NOP',0] for _ in range(77373)]
 for i,(old,_) in EDITS.items():source[i]=old
 source[DELETED[0]]=DELETED[1]
 for i,e in CUT_LITERALS.items():source[i]=e
 candidate=[];orig=[]
 for i,e in enumerate(source):
  if i==DELETED[0]:continue
  candidate.append(EDITS[i][1] if i in EDITS else e);orig.append(i)
  if i in INSERTS:candidate.extend(INSERTS[i]);orig.extend([None]*len(INSERTS[i]))
 need(bind_origins(source,candidate,orig),'positive origin')
 def reject(label,src,cand,origin):
  try:bind_origins(src,cand,origin)
  except ValueError:return label
  raise ValueError('origin control accepted '+label)
 extra=orig.copy();extra[0]=None
 wrong=source.copy();wrong[DELETED[0]]=['NOP',0]
 mutated=candidate.copy();mutated[0]=['NOP',1]
 inserted=candidate.copy();inserted[orig.index(None)]=['ADD',1394,264,'1/2',127]
 return {'positive':'exact deletion and 21 insertions accepted','rejected':[reject('extra_missing_origin',source,candidate,extra),reject('wrong_deleted_literal',wrong,candidate,orig),reject('mapped_mutation',source,mutated,orig),reject('inserted_mutation',source,inserted,orig)]}
def run():
 for p,h in PINS.items():need(sha(p.read_bytes())==h,'input pin '+str(p))
 spec=importlib.util.spec_from_file_location('independent_cert',CHECKER); v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 source=json.loads(gzip.decompress(SOURCE.read_bytes())); candidate=json.loads(gzip.decompress((BASE/'candidate-word.json.gz').read_bytes()))
 sc=json.loads(SCERT.read_bytes()); cc=json.loads((BASE/'candidate-certificates.json').read_bytes()); orig=json.loads((BASE/'origins.json').read_bytes())
 need(sha(canon(source))=='b80b6e74bff87c8d8160c5e121dac7c68df0827a7061847b896075417a346238','source canonical')
 need(sha(canon(candidate))=='1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e','candidate canonical')
 bind_origins(source['program'],candidate['program'],orig)
 need({k:x for k,x in source.items() if k!='program'}=={k:x for k,x in candidate.items() if k!='program'},'metadata')
 need(len(sc)==len(cc)==204,'denominator')
 def census(w):
  n=w['public']; p=w['program']; counts=Counter()
  for e in p:
   op,r=e[:2]
   if op in ('INIT','CLEAR') or (op=='MOVE' and r>=n):counts['owned']+=1
   if op=='CLEAR':counts['clears']+=1
   if op in ('ADD','COPY','SCALE') and (r>=n or (op!='SCALE' and e[2]>=n)):counts['interfaces']+=1
   if op=='COPY':counts['copies']+=1
  return dict(counts)
 need(census(source)==census(candidate)=={'owned':455,'clears':204,'interfaces':700,'copies':1},'fixed census')
 for a,b in zip(sc,cc):
  need(orig[b['event']]==a['event'] and orig[b['init_event']]==a['init_event'],'clear/init binding')
  need([[orig[m[0]],*m[1:]] for m in b['owned_moves']]==a['owned_moves'],'move binding')
  for key in ('event','init_event'):
   need(candidate['program'][b[key]]==source['program'][a[key]],'lifetime event literal')
  for x,y in zip(a['owned_moves'],b['owned_moves']):need(candidate['program'][y[0]]==source['program'][x[0]],'move literal')
  permitted={'event','init_event','owned_moves'}|({'certificate','terms'} if a['field']==1531 and a['event']==45133 else set())
  need({k:x for k,x in a.items() if k not in permitted}=={k:x for k,x in b.items() if k not in permitted},'record mapping')
 controls=v.controls(); origin_control=origin_controls(); a=v.replay(source,sc,1501,204,7)
 real=v.check_record; rejected=[]
 def guarded(c,*args):
  if c['field']==1531 and orig[c['event']]==45133:
   old=next(x for x in sc if x['field']==1531 and x['event']==45133)
   for label,coeff in [('old',old['certificate']),('wrong',dict(c['certificate'],**{'296':'1'}))]:
    bad=copy.deepcopy(c);bad['certificate']=coeff;bad['terms']=len(coeff)
    try:real(bad,*args)
    except ValueError as e:
     need('certificate relation mismatch' in str(e),label+' wrong failure');rejected.append(label)
    else:raise ValueError(label+' witness accepted')
  return real(c,*args)
 v.check_record=guarded
 b=v.replay(candidate,cc,1501,204,7)
 need(rejected==['old','wrong'],'actual witness controls');need(a['peak']==b['peak']==50,'peak')
 v.endpoint_guard(a['final_public_rows'],b['final_public_rows'])
 result={'status':'PASS_INDEPENDENT_CERTIFICATE_AND_REMAINING_LIVE_RANK_204','candidate_canonical_sha256':sha(canon(candidate)),'input_sha256':{str(p.relative_to(ROOT)):h for p,h in PINS.items()},'verifier_sha256':sha(Path(__file__).read_bytes()),'source_final_public_rank':a['final_public_rank'],'candidate_final_public_rank':b['final_public_rank'],'source_records':len(a['records']),'candidate_records':len(b['records']),'zero_records':7,'peak':50,'rank_argument':b['rank_argument'],'actual_witness_rejections':rejected,'origin_controls':origin_control,'controls':controls,'limitations':['remaining-live rank is not public-only rank at cuts','no physical erasure, supplier U, invoice or kappa admission']}
 out=HERE/'RESULT.json';need(not out.exists(),'result exists');out.write_bytes(canon(result)+b'\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':
 import sys
 if sys.argv[1:]==['--origin-controls-only']:
  print(json.dumps(origin_controls(),sort_keys=True));sys.exit(0)
 need(sys.argv[1:]==['--one-authorized-run'],'explicit launch argument required')
 fd=os.open(HERE/'RUN.started',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(fd,b'started\n');os.close(fd)
 resource.setrlimit(resource.RLIMIT_CPU,(2400,2400));resource.setrlimit(resource.RLIMIT_AS,(2**31,2**31));signal.alarm(3000)
 run()
