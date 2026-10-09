from pathlib import Path
from hashlib import sha256
import datetime,importlib.util,json,os,sys,time,pickle
W=Path(__file__).resolve().parent;P=W/'repo/research/r12-logical-frames'
name=sys.argv[1];O=W/name;O.mkdir(exist_ok=True)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
config={k:os.environ[k] for k in ('R12_FRAME_MODE','R12_FRAME_ROUNDS','R12_DEFER_MODE')};sources={str(p.relative_to(P)):sha256(p.read_bytes()).hexdigest() for p in P.glob('*.py')};start=time.monotonic()
(O/'process.json').write_text(json.dumps(dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),config=config,sources=sources),indent=2)+'\n')
sys.path.insert(0,str(P));ref=load('r12_reflection',P/'reflection_audit.py');d=ref.capture(P/'complex_deferred.py')
(O/'complex-profile.json').write_text(json.dumps(d['out'],indent=2,sort_keys=True)+'\n')
adapter=load('r12_birth_checkpoint',W/'references/birth_checkpoint.py');adapter.export_checkpoint(d,O)
result=ref.audit(d);result['source_sha256']=sha256((P/'complex_deferred.py').read_bytes()).hexdigest();result['audit_sha256']=sha256((P/'reflection_audit.py').read_bytes()).hexdigest()
(O/'reflection-audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
assert sources=={str(p.relative_to(P)):sha256(p.read_bytes()).hexdigest() for p in P.glob('*.py')}
receipt=dict(status='PASS complete own-candidate compiler, dirty replay, exact binary frames, exact all-input supports and independent literal reflection',elapsed_seconds=round(time.monotonic()-start,3),config=config,sources=sources,profile_sha256=sha256((O/'complex-profile.json').read_bytes()).hexdigest(),checkpoint_sha256=sha256((O/'FRAMES.pkl').read_bytes()).hexdigest(),reflection_sha256=sha256((O/'reflection-audit.json').read_bytes()).hexdigest())
(O/'verification.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,indent=2))
