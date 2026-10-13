"""Offline changed-complex finite replay and exact composition. Assertions required."""
from pathlib import Path
import sys,os,json,hashlib,tarfile,shutil,subprocess,time
if not __debug__:raise RuntimeError('Assertions must remain enabled')
P=Path(__file__).resolve().parent;O=Path(sys.argv[1]).resolve();assert not O.exists()and not O.is_relative_to(P)
m=json.loads((P/'MANIFEST.json').read_text());assert m=={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in P.rglob('*')if f.is_file()and f!=P/'MANIFEST.json'and '__pycache__'not in f.parts}
O.mkdir(parents=True);(O/'tmp').mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(O/'tmp'));start=time.monotonic()
with tarfile.open(P/'dependencies/sources.tar.gz')as t:
 for e in t:
  assert e.isfile();q=O/e.name;assert q.resolve().is_relative_to(O);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(t.extractfile(e).read())
for f in(P/'scripts').iterdir():shutil.copyfile(f,O/f.name)
commands=[('local',[O/'source541-static44/replay.py','--out',O/'static44-local314']),('global',[O/'verify_static44_global.py',O/'global']),('price',[O/'price_static44_composition.py',O/'global',O/'PRICE.json'])]
for name,args in commands:
 with(O/(name+'.log')).open('w')as f:subprocess.run([sys.executable,'-B',*map(str,args)],env=env,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True)
 print('PASS',name,flush=True)
x=json.loads((O/'PRICE.json').read_text());expected=json.loads((P/'EXPECTED.json').read_text())
# Generated gzip headers differ by Python version; every actual template hash
# is bound inside its own fresh owner and invoice audits. Compare exact math.
assert {k:v for k,v in x.items()if k!='complex_template_sha256'}=={k:v for k,v in expected.items()if k!='complex_template_sha256'}
r=dict(status='PASS_PACKAGED_CHANGED_COMPLEX_AND_EXACT_COMPOSITION',kappa=x['kappa_decimal'],complex=x['complex_decimal'],bit=x['bit_lower'],python=sys.version,seconds=time.monotonic()-start,manifest_sha256=hashlib.sha256((P/'MANIFEST.json').read_bytes()).hexdigest(),scope=x['scope']);(O/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa'])
