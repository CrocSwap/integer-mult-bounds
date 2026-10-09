#!/usr/bin/env python3
"""Independent literal binding of output records to the paid scatter word.

This check is deliberately separate from the inherited replay. It does not
establish all-size tape transfer, profile completeness, or an asymptotic bound.
"""
import gzip,hashlib,importlib.util,json,pathlib,subprocess,sys,time
if sys.flags.optimize:
 raise RuntimeError('Run without -O: assertions are part of this checker')
from collections import Counter
from itertools import combinations
ROOT=pathlib.Path(__file__).resolve().parents[2]
REPO=ROOT/'work/agents/repository-audit/repo'
OUT=ROOT/'outputs/audit'
WORK=ROOT/'work/agents/repository-audit/replay-bindings'
PINS={
 'pr57':('47916b3bf2895c117f8b53ffff4732f67178a132','certificates/skip-frame-word-{h}.json.gz'),
 'pr58':('96c52fb81cab6e714768e00ca33ca7f004ebcac4','certificates/joint-dual-word-{h}.json.gz'),
 'pr60':('e7a492dd8bee4e6f574ced784a62af2ce735edc4','certificates/joint-dual-word-{h}.json.gz'),
 'pair_assembly':('ad0f25ff7b23cff7f08ad237c2254e6ecf74257e','research/pair-assembly/frame/frame-word-{h}.json.gz'),
}
def blob(pin,path):return subprocess.run(['git','-C',str(REPO),'show',f'{pin}:{path}'],check=True,capture_output=True).stdout

def verify_scatter(d):
 h,v,R=d['h'],d['v'],d['R'];triples=list(combinations(range(h),3));assert len(triples)==v
 assert set(map(int,d['sources']))==set(range(v))
 assert all(isinstance(s,int) and 0<=s<R for s in d['sources'].values())
 assert len(set(d['sources'].values()))==v
 expected=[];seen=set();central=0
 for slot,frame,common,triple in d['outputs']:
  assert isinstance(slot,int) and 0<=slot<R and slot not in seen;seen.add(slot)
  assert isinstance(frame,int) and 0<=frame<len(d['frames'])
  assert 0<=common<h
  if len(triple)==1:
   assert triple==[common];central+=1
   destinations=[i for i,t in enumerate(triples) if common in t]
  else:
   assert len(triple)==3 and list(triple)==sorted(triple) and common in triple
   destinations=[triples.index(tuple(triple))]
  expected.extend([v+i,2*v+slot] for i in destinations)
 assert central==h
 for target,source in d['scatter']:
  assert v<=target<2*v and 2*v<=source<2*v+R
 assert d['scatter']==expected,'Serialized scatter differs from complete output-derived literal operation list'
 return {'scatter_xors':len(expected),'central_outputs':central,'output_records':len(d['outputs']),
         'literal_binding':True,'sequence_sha256':hashlib.sha256(json.dumps(expected,separators=(',',':')).encode()).hexdigest()}

def main():
 WORK.mkdir(parents=True,exist_ok=True)
 assert subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()==PINS['pair_assembly'][0]
 report={'scope':'Source-to-serialized-scatter binding only; not a complete finite or asymptotic proof.', 'axes':[]}
 for name,(pin,template) in PINS.items():
  for h in (23,25):
   path=template.format(h=h)
   try:raw=blob(pin,path)
   except subprocess.CalledProcessError as e:
    report['axes'].append({'name':name,'h':h,'error':e.stderr.decode()});continue
   d=json.loads(gzip.decompress(raw));r=verify_scatter(d)
   r.update(candidate=name,pin=pin,path=path,compressed_sha256=hashlib.sha256(raw).hexdigest())
   report['axes'].append(r);print('PASS',name,h,r['scatter_xors'],flush=True)
 # Build a counterexample for the checker-interface, not for actual generated words:
 # add the same otherwise uncharged scratch-to-output XOR twice. It is identity
 # on arbitrary state, so the inherited algebraic replay accepts it, yet the
 # output list does not charge or describe these literal incidences.
 pin,path=PINS['pair_assembly'];path=path.format(h=23);raw=blob(pin,path);d=json.loads(gzip.decompress(raw))
 out={s for s,_,_,_ in d['outputs']};s=next(i for i in range(d['R']) if i not in out)
 rogue=[d['v'],2*d['v']+s];d['scatter'].extend([rogue,rogue])
 mutant=WORK/'duplicate-uncharged-scatter.json.gz';mutant.write_bytes(gzip.compress(json.dumps(d).encode(),mtime=0))
 rejected=False
 try:verify_scatter(d)
 except AssertionError:rejected=True
 assert rejected
 spec=importlib.util.spec_from_file_location('inherited_replay',REPO/'scripts/experiments/binary_frame_replay.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 start=time.time();legacy=m.replay(mutant)
 report['mutation']={'kind':'two identical unrecorded auxiliary-to-output XORs','added_gates':2,
   'legacy_replay_accepts':True,'strict_binding_rejects':rejected,'replay_seconds':time.time()-start,
   'actual_candidate_invalidated':False,'legacy_receipt':legacy,
   'conclusion':'The inherited replay lacks literal scatter/output binding. All actual candidate words above pass the strengthened binding; the mutation demonstrates checker incompleteness, not a wrong claimed exponent.'}
 (OUT/'scatter-binding-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS strengthened binding; inherited checker accepts adversarial duplicate gates',flush=True)
if __name__=='__main__':main()
