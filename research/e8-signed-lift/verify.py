#!/usr/bin/env python3
"""Reconstruct, audit and price this own changed construction. No public baseline replay."""
import argparse,hashlib,json,os,pathlib,subprocess,sys,zipfile
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('Assertions must remain enabled')
ROOT=pathlib.Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=pathlib.Path);ap.add_argument('--cxx',default='g++');ap.add_argument('--boost-include',type=pathlib.Path);a=ap.parse_args()
out=a.output.resolve()
if out.exists():raise SystemExit('Choose a new output directory; no existing results are removed')
files=json.loads((ROOT/'MANIFEST.json').read_text())['files']
actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.rglob('*')if p.is_file()and p.name!='MANIFEST.json'}
assert actual==files,'Package source missing, changed or unlisted'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1');py=[sys.executable,'-X','utf8','-B']
cmd=py+[str(ROOT/'code/verify-own.py'),'--package-root',str(ROOT),'--output',str(out),'--cxx',a.cxx]
if a.boost_include:cmd+=['--boost-include',str(a.boost_include)]
subprocess.run(cmd,check=True,env=env)
with zipfile.ZipFile(ROOT/'vendor/e8-public352.zip')as z:
 names=z.namelist();assert len(names)==len(set(names))
 for n in names:
  q=pathlib.PurePosixPath(n);assert not q.is_absolute()and '..'not in q.parts
  target=out/'e8'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(n))
# The unchanged E8 published receipt is explicit input. Do not silently count it as our re-verification.
subprocess.run(py+[str(ROOT/'code/price-final.py'),str(out/'final'),str(out/'PRICE.json'),str(out/'BANK.json'),str(out/'e8/code/pricing')],check=True,env=env)
exe=out/'bin'/('invoice-own.exe'if os.name=='nt'else'invoice-own')
cmd=[a.cxx,'-O3','-std=c++17','-I',str(ROOT/'code')]
if a.boost_include:cmd+=['-I',str(a.boost_include)]
subprocess.run(cmd+[str(ROOT/'code/invoice-own.cpp'),'-o',str(exe)],check=True,env=env)
subprocess.run([str(exe),str(out/'final/records.bin'),str(out/'PRICE.json'),str(out/'BANK.json'),str(out/'COLUMNS.json'),str(out/'INVOICE.json')],check=True,env=env)
price=json.loads((out/'PRICE.json').read_text());assert price['kappa']=='801967436473393/1000000000000000000'
receipt=dict(status='PASS_OWN_LITERAL_CONSTRUCTION_EXACT_PRICE_AND_FINITE_INVOICE',kappa=price['kappa'],bit_coarse=price['bit_coarse'],complex_coarse=price['complex_coarse'],word_sha256=price['source_word_sha256'],manifest_sha256=hashlib.sha256((ROOT/'MANIFEST.json').read_bytes()).hexdigest(),public_baseline_mathematical_verification_replayed=False,unchanged_complex_supplier_reverified=False,receipt_hashes={n:hashlib.sha256((out/n).read_bytes()).hexdigest()for n in ['OWN-VERIFICATION.json','PRICE.json','INVOICE.json','SIGNED-TARGET.json','SOURCE-SPANS.json','COLUMNS.json','BANK.json','NEW-FRAME-PRIMES.json','REFLECTED-LEDGERS.json','EVEN-LIFT-CONTROL.json']},scope=price['scope'])
(out/'RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
assert actual=={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.rglob('*')if p.is_file()and p.name!='MANIFEST.json'}
print('PASS conditional kappa',price['kappa'],flush=True)
