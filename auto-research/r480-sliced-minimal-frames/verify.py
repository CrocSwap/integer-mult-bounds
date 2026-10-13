"""Reproduce scalar/frame transformation and prospective arithmetic; physical admission separate.
Prepared for rohanarun with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import os,sys,json,hashlib,shutil,subprocess,gzip,time,argparse,tarfile
if not __debug__:raise RuntimeError('Assertions must remain enabled')
ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);ap.add_argument('--physical',action='store_true');ap.add_argument('--boost-include',default='/usr/include');ap.add_argument('--cxx',default='c++');args=ap.parse_args();P=Path(__file__).resolve().parent;O=args.out.resolve();assert not O.exists() and not O.is_relative_to(P)
manifest=json.loads((P/'MANIFEST.json').read_text());assert manifest=={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in P.rglob('*')if f.is_file()and f!=P/'MANIFEST.json'and '__pycache__'not in f.parts}
O.mkdir(parents=True);(O/'tmp').mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(O/'tmp'));start=time.monotonic()
w=O/'bit510-review/research/e8-r480-dead-totals/data';w.mkdir(parents=True);shutil.copyfile(P/'inputs/ORIGINAL.json.gz',w/'bitE8mut-r480.json.gz')
a=O/'r480-sharp535-publication/research/r480-sharp-charge535';(a/'inputs').mkdir(parents=True);shutil.copytree(P/'engines',a/'engines')
for name in ['PR510-EXPECTED.json','PR535-EXPECTED.json']:shutil.copyfile(P/'inputs'/name,a/'inputs'/name)
shutil.copyfile(P/'inputs/PR539-EXPECTED.json',a/'EXPECTED.json')
for name in ['slice','minimum','price']:
 f=O/(name+'.py');shutil.copyfile(P/'scripts'/(name+'.py'),f)
 with (O/(name+'.log')).open('w')as log:subprocess.run([sys.executable,'-B',str(f)],cwd=O,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 print(name,'PASS',flush=True)
new=O/'bit510-sliced-minimal-frames/WORD.json.gz';assert json.loads(gzip.decompress(new.read_bytes()))==json.loads(gzip.decompress((P/'inputs/BASE-CANDIDATE.json.gz').read_bytes()))
x=json.loads((O/'bit510-sliced-minimal-price/RESULT.json').read_text());assert x==json.loads((P/'inputs/BASE-EXPECTED.json').read_text())
m=json.loads((O/'bit510-sliced-minimal-frames/RESULT.json').read_text());e=json.loads((P/'evidence/MINIMUM-FRAMES.json').read_text());assert {k:v for k,v in m.items()if k not in ('seconds','fee_delta')}=={k:v for k,v in e.items()if k not in ('seconds','fee_delta')}  # libm discovery diagnostic only; all frames/profiles and subsequent rational pricing remain exact
# Reconstruct PR541 exactly, then retain only the frozen beneficial frame reductions.
f=O/'preload60.py';shutil.copyfile(P/'scripts/preload60.py',f)
with (O/'preload60.log').open('w')as log:subprocess.run([sys.executable,'-B',str(f),'--input',str(w/'bitE8mut-r480.json.gz'),'--out',str(O/'trace541-rebuild')],cwd=O,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
assert json.loads(gzip.decompress((O/'trace541-rebuild/WORD.json.gz').read_bytes()))==json.loads(gzip.decompress((P/'inputs/PR541-WORD.json.gz').read_bytes()))
for name in ['trace_slice','transfer','profile','trace_price']:
 f=O/(name+'.py');shutil.copyfile(P/'scripts'/(name+'.py'),f)
 with (O/(name+'.log')).open('w')as log:subprocess.run([sys.executable,'-B',str(f)],cwd=O,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 print(name,'PASS',flush=True)
new=O/'trace541-frozen-minimum/WORD.json.gz';assert json.loads(gzip.decompress(new.read_bytes()))==json.loads(gzip.decompress((P/'inputs/CANDIDATE.json.gz').read_bytes()))
x=json.loads((O/'trace541-frozen-minimum-price/RESULT.json').read_text());assert x==json.loads((P/'EXPECTED.json').read_text())
subprocess.run([sys.executable,'-B',str(P/'scripts/final_arithmetic.py'),str(P),str(O/'FINAL-ARITHMETIC.json')],cwd=O,env=env,check=True)
r=dict(status='PASS_PACKAGED_RECONSTRUCTION_AND_PROSPECTIVE_PRICE',kappa=x['kappa_decimal'],bit=x['bit_decimal'],word_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),manifest_sha256=hashlib.sha256((P/'MANIFEST.json').read_bytes()).hexdigest(),python=sys.version,seconds=time.monotonic()-start,scope='Exact reconstruction of source slice and least frames,720 scalar columns, nesting and two rational moment engines with47 outer constraints. Prospective unchanged owner schedule and prior finite allowances; physical template and finite invoice remain pending. No completed supplier admission.')
(O/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa'],flush=True)

if args.physical:
 for archive in ['source493.tar.gz','source510.tar.gz']:
  with tarfile.open(P/'dependencies'/archive)as t:
   for item in t:
    if item.isdir():continue
    assert item.isfile(),item.name
    p=O/item.name;assert p.resolve().is_relative_to(O)
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(item).read())
 f=O/'physical.py';shutil.copyfile(P/'scripts/physical.py',f)
 env.update(BOOST_INCLUDE=args.boost_include,CXX=args.cxx)
 with (O/'physical.log').open('w')as log:subprocess.run([sys.executable,'-B',str(f)],cwd=O,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 physical=json.loads((O/'trace541-frozen-admission/RESULT.json').read_text());assert physical['kappa']==x['kappa_decimal'] and physical['profile']==x['profile']
 r.update(status='PASS_PACKAGED_CONSTRUCTION_PHYSICAL_ADMISSION_AND_EXACT_PRICE',physical_receipt='trace541-frozen-admission/RESULT.json',seconds=time.monotonic()-start,scope='Fresh complete finite record, geometry, owner and invoice replay plus exact source reconstruction and two-engine pricing. Complex535 cited rather than rebuilt; inherited all-size assumptions remain conditional.')
 (O/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['kappa'],flush=True)
