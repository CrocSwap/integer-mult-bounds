"""Offline complex-stage composition verification; PR493 bit receipt is cited.
Default rebuilds the pinned complex provider and both local words freshly.
Explicit --reuse-local accepts only the published byte-pinned completed replay.
"""
from pathlib import Path
import argparse,json,gzip,hashlib,shutil,subprocess,os,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);ap.add_argument('--reuse-provider',type=Path);ap.add_argument('--reuse-local',type=Path);a=ap.parse_args();O=a.out.resolve();assert not O.exists() and not O.is_relative_to(ROOT)
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(p):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
actual=inventory(ROOT);actual.pop('MANIFEST.json');assert actual==read(ROOT/'MANIFEST.json');O.mkdir();steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
def run(name,script,*args):
 log=O/(name+'.log');t=time.monotonic()
 with log.open('w') as f:q=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,returncode=q.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));(O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n');assert q.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
try:
 if a.reuse_provider:
  p=a.reuse_provider.resolve();pins=read(ROOT/'REUSE-PROVIDER-INPUTS.json');assert all(sha(p/k)==v for k,v in pins.items());assert read(p/'RECEIPT.json')['status']=='PASS_FULL_COMPLEX_GAUGE_KERNEL_COMPOSITION';shutil.copytree(p,O/'provider')
 else:run('provider',ROOT/'vendor/complex/e8-complex-gauge-kernel/verify.py',O/'provider')
 run('frozen-baseline',ROOT/'code/apply_retime.py',O/'provider/gauge80-kernel42/split-centres/FULL-WORD.json.gz',ROOT/'data/RETIME-FRAMES.json.gz',O/'REBUILT-BASE.json.gz');assert read(O/'REBUILT-BASE.json.gz')==read(ROOT/'data/BASE-WORD.json.gz')
 sys.path.insert(0,str(ROOT/'code'));import gk_word as G
 raw=read(O/'provider/gauge80-kernel42/sc_base/FULL-WORD.json.gz');base=read(O/'REBUILT-BASE.json.gz');n=len(base['A'])-len(raw['A']);assert n==531
 assert [e[:-1] for e in raw['A']]==[e[:-1] for e in base['A'][n:]] and [e[:-1] for e in raw['B']]==[e[:-1] for e in base['B']]
 raw['A']=base['A'][n:];raw['B']=base['B'];raw['cleanup']=[G.inverse(e,G.FULL) for e in reversed(raw['A']+raw['B']) if not 120<=e[1]<240];middle=G.build(raw,read(ROOT/'data/STAGE4-SELECTION.json'));assert middle==read(ROOT/'data/STAGE4-WORD.json.gz')
 if a.reuse_local:
  p=a.reuse_local.resolve();pins=read(ROOT/'REUSE-LOCAL-INPUTS.json');assert all(sha(p/k)==v for k,v in pins.items());assert read(p/'RECEIPT.json')['status']=='PASS_BOTH_LOCAL_WORDS_NO_MIXED_GLOBAL_ADMISSION';shutil.copytree(p,O/'local')
 else:run('local-words',ROOT/'verify_local.py',O)
 run('mixed-emitter',ROOT/'emit_mixed.py',O);run('mixed-independent-audit',ROOT/'audit_mixed.py',O);run('mixed-invoice',ROOT/'audit_invoice.py',O);run('arithmetic',ROOT/'verify_arithmetic.py',O/'arithmetic')
 got=read(O/'arithmetic/EXACT-ARITHMETIC.json');expected=read(ROOT/'EXACT-ARITHMETIC.json');assert got==expected
 own=read(O/'mixed/AUDIT.json');invoice=read(O/'mixed/invoice/MIXED-INVOICE.json');assert got['profile']==own['profile'] and invoice['retained_row_coefficient']==20161 and invoice['retained_payload_bits']==192
 receipt=dict(status='PASS_COMPLEX_STAGE_DEPENDENT_FINITE_COMPOSITION',kappa=got['kappa'],complex_lower=got['complex_lower'],provider_mode='completed-replay-reuse' if a.reuse_provider else 'fresh',local_mode='published-byte-pinned-reuse' if a.reuse_local else 'fresh',bit_mode='PR493 source-pinned receipt cited, not freshly replayed',steps=steps,artifacts={str(p.relative_to(O)):sha(p) for p in [O/'mixed/AUDIT.json',O/'mixed/invoice/MIXED-INVOICE.json',O/'arithmetic/EXACT-ARITHMETIC.json',O/'local/RECEIPT.json']},scope='Finite conditional complex composition with exact source-pinned bit input. All-size compiler/common-label, Lemma A realization, restored-row, precision/tape and analytic-transfer contracts remain inherited.')
 (O/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],got['kappa_decimal'],flush=True)
except BaseException as e:
 (O/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
