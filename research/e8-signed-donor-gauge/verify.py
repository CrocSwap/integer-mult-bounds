from pathlib import Path
import json,hashlib,os,sys,subprocess,gzip,ast,types,copy,shutil
from fractions import Fraction as Q
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.load(open(ROOT/'MANIFEST.json'))
assert {str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json'}==expected
out=Path(sys.argv[1]).resolve();assert not out.exists() and ROOT not in out.parents and out not in ROOT.parents
assert shutil.disk_usage(out.parent).free>6_000_000
out.mkdir();(out/'tmp').mkdir()
for rel in expected:
 src=ROOT/rel;dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);os.link(src,dest)
os.chdir(out);P=Path('pr378-donor-screen');sys.path.insert(0,str(out/'pr378-complex-screen/package/code'));import cxkernel as C
src=P/'pr395-small/construct.py';tree=ast.parse(src.read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='transform');ns=dict(Q=Q,copy=copy,defaultdict=defaultdict,up=types.SimpleNamespace(rehist=C.rehist));exec(compile(ast.Module(body=[fn],type_ignores=[]),'pinned_transform','exec'),ns)
old=json.load(gzip.open('pr378-complex-screen/package/data/gcert1-e8-r783-far.json.gz'));candidate=ns['transform'](old,json.load(open(P/'pr395-small/SELECTION.json')));blob=json.dumps(candidate,sort_keys=True,separators=(',',':')).encode();assert hashlib.sha256(blob).hexdigest()==json.load(open(P/'pr395-small/EXPECTED-DISCOVERY.json'))['candidate_sha256'];(P/'signed25.json.gz').write_bytes(gzip.compress(blob,mtime=0))
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(out/'tmp'));checks=[]
for name in ['check_signed25_composition','check_signed25_gauge_lift','emit_signed25_gauge','audit_signed25_gauge','integrate_signed25','audit_signed25_global','assemble_signed25']:
 print('RUN',name,flush=True)
 with (out/(name+'.log')).open('w') as f:subprocess.run([sys.executable,'-B',str(P/(name+'.py'))],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 checks.append(dict(name=name,log_sha256=sha(out/(name+'.log'))))
assert all(sha(ROOT/rel)==digest for rel,digest in expected.items())
r=json.load(open(P/'signed25-assembly.json'));a=json.load(open(P/'signed25-integration.json'));result=dict(status='PASS_FRESH_STANDALONE_CHANGED_COMPLEX_AND_EXACT_ASSEMBLY',checks=checks,template_sha256=a['template_sha256'],kappa=r['kappa'],complex_coarse=r['complex_coarse'],bit_coarse=r['bit_coarse'],input_manifest_sha256=sha(ROOT/'MANIFEST.json'),scope='All seven changed-candidate stages freshly executed from immutable vendored inputs; baseline local Clifford proofs and bit386 receipt reused through binding, not freshly executed. No full all-source proof, Lean or ready claim. Full inherited bit/supplier replay and CI remain before readiness.')
(out/'VERIFICATION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
