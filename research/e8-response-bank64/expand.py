"""Replicate the pinned nine-stage data skeleton; retain every local program."""
from pathlib import Path
import copy,gzip,hashlib,json,sys
assert __debug__
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'e8-response-subspaces'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]);assert not out.exists();out.mkdir(parents=True)
 original=SOURCE/'architecture/inputs/GLOBAL-TEMPLATE.json.gz'
 p=json.loads(gzip.decompress(original.read_bytes()));c=read(SOURCE/'inputs/candidate781.json');cfg=read(ROOT/'CONFIG.json')
 v,R,h=c['v'],c['R'],c['h'];T=cfg['replicas'];stages=[e for e in p['recipe'] if e['kind']=='local'];L=len(stages);pairs=len({e['pair'] for e in stages});oldT=len({x['replica'] for x in p['calls']});slots=(p['m']-1)//h
 assert p['m']==slots*h+1 and T%oldT==0 and T*R%slots==0
 def owners(call,rep,replicas):
  data=2*pairs*v*replicas;bank=replicas*R//slots;s=call['stage'];pair=call['pair']
  return [[rep*2*pairs*v+(2*pair+r//v)*v+r%v,[1,s,r%v]] for r in range(2*v)]+[[data+s*bank+(rep*R+k)//slots,[2,(rep*R+k)%slots]] for k in range(R)]
 # Decode and validate the original complete schedule before replication.
 assert len(p['calls'])==L*oldT and {(x['stage'],x['replica']) for x in p['calls']}=={(s['stage'],r) for s in stages for r in range(oldT)}
 for call in p['calls']:
  assert call['owners']==owners(call,call['replica'],oldT)
  event=next(e for e in stages if e['stage']==call['stage'])
  assert call['pair']==event['pair'] and call['orientation']==('backward' if event['reverse'] else 'forward')
  assert call['local_program_sha256']==hashlib.sha256(''.join(json.dumps(e,separators=(',',':'))+'\n' for e in p['local_programs'][call['orientation']]).encode()).hexdigest()
 q=copy.deepcopy(p);q['calls']=[]
 for event in stages:
  exemplar=next(x for x in p['calls'] if x['stage']==event['stage'] and x['replica']==0)
  for rep in range(T):
   call=copy.deepcopy(exemplar);call['replica']=rep;call['owners']=owners(call,rep,T);q['calls'].append(call)
 for ch in q['idle_children']:assert ch['replicas']==oldT;ch['replicas']=T
 data=2*pairs*v*T;bank=T*R//slots;live=data+L*bank;physical=live+R+h+1
 q.update(live=live,physical=physical,private_namespace=dict(centers=[live,live+h],tableau=[live+h,live+h+R],coefficient=[physical-1,physical]))
 q['bank_padding']['families']=list(range(data,live));q['cover_final_correction']['families']=[0,live];q['cover_final_correction']['charged_calls_per_cover']=live
 for event in q['execution_schedule']:
  if event['kind']=='local_cover_sweep':assert event['replicas']==list(range(oldT));event['replicas']=list(range(T))
  elif event['kind']=='bank_padding_cover_sweep':event['families']=[data,live]
  elif event['kind']=='translate_every_live_family':event.update(q['cover_final_correction'])
 def audit(t):
  assert len(t['calls'])==L*T and {(x['stage'],x['replica']) for x in t['calls']}=={(s['stage'],r) for s in stages for r in range(T)}
  for x in t['calls']:assert x['owners']==owners(x,x['replica'],T)
  assert all(ch['replicas']==T for ch in t['idle_children'])
  assert t['recipe']==p['recipe'] and t['local_programs']==p['local_programs'] and t['exact_data_phase_recipe_sha256']==sha(SOURCE/'architecture/inputs/DATA-PHASES.json')
 audit(q);controls=[]
 for name,mut in [('missing_replica',lambda t:t['calls'].pop()),('aliased_data_owner',lambda t:t['calls'][0]['owners'].__setitem__(1,t['calls'][0]['owners'][0])),('wrong_idle_replication',lambda t:t['idle_children'][0].__setitem__('replicas',oldT))]:
  t=copy.deepcopy(q);mut(t)
  try:audit(t)
  except AssertionError:controls.append(name)
  else:raise AssertionError('accepted '+name)
 raw=json.dumps(q,sort_keys=True,separators=(',',':')).encode();(out/'PRIOR.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 result=dict(status='PASS_SOURCE_BOUND_REPLICA_EXPANSION',replicas=T,calls=L*T,data_families=data,source_sha256=sha(original),template_sha256=hashlib.sha256(raw).hexdigest(),controls_rejected=controls,source_hashes={str(p):sha(p) for p in [original,ROOT/'CONFIG.json',Path(__file__)]})
 (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
