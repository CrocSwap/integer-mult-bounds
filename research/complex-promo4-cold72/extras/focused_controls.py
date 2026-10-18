"""Independent native rejection controls for each of the six nominated ends."""
from pathlib import Path
import json,gzip,copy,tempfile,importlib.util,argparse,time
P=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('audit',P/'local/hpe_audit_and_transport.py');audit=importlib.util.module_from_spec(s);s.loader.exec_module(audit)
ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(exist_ok=False)
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
w=read(args.word);v=w['report']['v'];npre=w['refactored_cleanup']['premix_gates'];routing=P/'vendor/main/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz';records=read(P/'data/NEW-ENDS.json');added={r['helper']for r in records};assert len(added)==6 and added<=set(map(int,w['helper_final']))

controls=[];start=time.monotonic()
def trial(word):
 with tempfile.TemporaryDirectory()as td:
  p=Path(td)/'word.json.gz';p.write_bytes(gzip.compress(json.dumps(word).encode(),mtime=0))
  try:audit.run(p,routing,Path(td)/'native');return None
  except AssertionError as e:return repr(e.args[0])if e.args else 'AssertionError'
assert trial(w)is None,'positive native word'
def reject(label,fn,reasons):
 z=copy.deepcopy(w);fn(z);error=trial(z);assert error is not None and any(t in error for t in reasons),(label,error,reasons);controls.append(dict(name=label,rejected=error));print('PASS',label,flush=True)
endpoint=['arbitrary-dirt endpoint'];dirty=['cold hyperplane-ended helper','arbitrary-dirt endpoint']
for record in records:
 h=record['helper'];tail=record['newtail'];gate=next(e for e in tail if e[0]=='add'and e[1]==h);index=next(i for i,f in w['early_cleanup']if w['cleanup'][i]==gate)
 reject(str(h)+'-end-removed',lambda z,h=h:z['helper_final'].pop(str(h)),['paid local profile differs'])
 wrong=next(f for key,f in w['helper_final'].items()if len(f)==8 and audit.basis(f)!=audit.basis(w['helper_final'][str(h)]))
 reject(str(h)+'-wrong-terminal-frame',lambda z,h=h,f=wrong:z['helper_final'].__setitem__(str(h),f),['hpe cone pre-check','nonmonotone'])
 reject(str(h)+'-tail-zeroed',lambda z,i=index:z['cleanup'][i].__setitem__(3,0),endpoint)
 def drop(z,i=index):
  z['cleanup'].pop(i);z['early_cleanup']=[[j-(j>i),f]for j,f in z['early_cleanup']if j!=i]
 reject(str(h)+'-tail-dropped',drop,endpoint)
 fix=next((e for e in record['repair']if e[0]=='add'),None)
 if fix is not None:
  at=next(i for i,e in enumerate(w['A'][:npre])if e==fix)
  reject(str(h)+'-rankzero-repair-doubled',lambda z,i=at:z['A'][i].__setitem__(3,2*z['A'][i][3]),dirty)
 if record['target_compensation']:
  gate=record['target_compensation'][0];at=next(i for i,e in enumerate(w['A'][:npre])if e==gate)
  reject(str(h)+'-target-compensation-dropped',lambda z,i=at:z['A'].pop(i),['cold hyperplane-ended helper'])
(args.out/'CONTROLS.json').write_text(json.dumps(dict(status='PASS_LAYERED_SIX_END_NATIVE_CONTROLS',positive=1,helpers=sorted(added),rejected=controls,seconds=time.monotonic()-start),indent=2)+'\n');print('PASS',len(controls),'mutations')
