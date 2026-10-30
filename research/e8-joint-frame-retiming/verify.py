"""Verify the selected two-supplier composition using Python's standard library."""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
assert __debug__, 'Assertions must remain enabled'
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('output',type=Path,help='A new output directory outside this package')
ap.add_argument('--replay-phases',action='store_true',help='Recompute all selected Gaussian phase pairs instead of reusing their source-bound evidence')
a=ap.parse_args();out=a.output.resolve()
assert not out.exists() and not out.is_relative_to(ROOT)
def snapshot():
 return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
manifest=json.loads((ROOT/'MANIFEST.json').read_text());assert snapshot()==manifest['files'],'Source manifest mismatch'
sources=json.loads((ROOT/'SOURCES.json').read_text())
for z in sources['imported_files']:
 data=(ROOT/z['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==z['sha256']
 if 'source_sha256' in z:assert hashlib.sha256(gzip.decompress(data)).hexdigest()==z['source_sha256']
out.mkdir(parents=True)
def copy(src,dst):
 p=out/dst;p.parent.mkdir(parents=True,exist_ok=True)
 data=(ROOT/src).read_bytes();p.write_bytes(gzip.decompress(data) if src.endswith('.gz') and not dst.endswith('.gz') else data)
for src,dst in [
 ('inputs/e8-r865.json.gz','work/pr370-source/research/e8-bit/data/bit/bitE8-r865.json.gz'),
 ('inputs/complex-ports.json.gz','work/higher-stage-e8/verified/gcert1-e8-retimed.json.gz'),
 ('inputs/complex-template.json.gz','work/complex-nine-native/GLOBAL-TEMPLATE.json.gz'),
 ('inputs/complex-data-phases.json.gz','work/complex-nine-native/DATA-PHASES.json'),
 ('inputs/bit-geometry.json.gz','inherited/bit-geometry.json.gz'),
 ('vendor/clifford_exact.py','work/odd-stages/clifford_exact.py')]:copy(src,dst)
for name in ('moment','base_two_moment','outer'):copy('vendor/engines/'+name+'.py','work/pr361/code/engines/'+name+'.py')
p=out/'bit426-source-centres';p.mkdir()
env=dict(os.environ,E8_OUTPUT=str(out),E8_REPLAY_PHASES=str(int(a.replay_phases)),PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
steps=[]
def run(name,file,*args):
 with (out/(name+'.log')).open('w') as log:
  r=subprocess.run([sys.executable,'-B',str(ROOT/file),*map(str,args)],cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,str(out/(name+'.log')))
 steps.append(name);print('PASS',name,flush=True)
run('hamming_packets','vendor/hamming_packets.py')
for name in ('complex_construct','complex_audit','complex_emit','complex_phases','bit_construct','bit_kernel'):run(name,'code/'+name+'.py')
run('bit_export','vendor/export_records.py',p/'bit-source-centres.json',p/'records')
run('bit_global','code/bit_global.py','--source',p,'--local-check',p,'--out',p/'global')
run('bit_audit','code/bit_audit.py','--local-check',p,'--out',p/'global')
for name in ('bit_price','complex_integrate','complex_replay','combined'):run(name,'code/'+name+'.py')
run('independent_audit','code/independent_audit.py',ROOT,out,out/'INDEPENDENT-AUDIT.json')
assert snapshot()==manifest['files'],'Package modified during verification'
r=json.loads((out/'RESULT.json').read_text());expected=json.loads((ROOT/'EXPECTED.json').read_text())
for key,value in expected.items():assert r[key]==value,(key,r[key],value)
r['verification_steps']=steps;r['phase_mode']='full replay' if a.replay_phases else 'source-bound unchanged evidence';r['manifest_sha256']=hashlib.sha256((ROOT/'MANIFEST.json').read_bytes()).hexdigest()
(out/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS conditional kappa',r['kappa_decimal'])
