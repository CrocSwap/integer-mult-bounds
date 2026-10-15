"""Offline bit source closure and fresh integration into the retained PR396 assembly.
No historical PR370 or PR377 pipeline is rerun; their receipts are explicitly bound.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,os,subprocess,sys,shutil,time,importlib.util,gzip
assert __debug__
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def inventory(root):return {str(p.relative_to(root)):sha(p) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve()
assert not out.exists() and ROOT not in out.parents and out not in ROOT.parents
manifest=read(ROOT/'MANIFEST.json');actual=inventory(ROOT);actual.pop('MANIFEST.json');assert actual==manifest
pins=read(ROOT/'bit-nine-source/PINS.json');assert inventory(ROOT/'bit-source')==pins['bit_files']
own=inventory(ROOT/'bit-nine-source');own.pop('MANIFEST.json');assert own==read(ROOT/'bit-nine-source/MANIFEST.json')['files']
bind=read(ROOT/'BASELINE-BINDINGS.json')['files']
for rel,digest in bind.items():
 p=(ROOT/'retained-local'/rel) if (ROOT/'retained-local'/rel).exists() else ROOT/'bit-source'/rel
 assert sha(p)==digest,(rel,'baseline binding')
# Original record manifest independently binds every retained exported record.
for line in (ROOT/'bit-source/data/bit/RECORD-SHA256SUMS').read_text().splitlines():
 digest,rel=line.split();assert sha(ROOT/'retained-local/records'/rel)==digest
assert shutil.disk_usage(out.parent).free>25_000_000
out.mkdir();(out/'tmp').mkdir();steps=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(out/'tmp'))
try:
 for name,args in [
  ('geometry',['--source',str(ROOT/'bit-source')]),
  ('global_word',['--source',str(ROOT/'bit-source'),'--local-check',str(ROOT/'retained-local')]),
  ('audit',['--local-check',str(ROOT/'retained-local')]),
  ('certify',['--source',str(ROOT/'bit-source'),'--complex-check',str(ROOT/'retained-complex377')])]:
  t=time.monotonic();print('RUN',name,flush=True)
  with (out/(name+'.log')).open('w') as f:
   subprocess.run([sys.executable,'-B',str(ROOT/'bit-nine-source'/(name+'.py')),*args,'--out',str(out/'bit-nine')],cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  steps.append(dict(name=name,seconds=time.monotonic()-t,log_sha256=sha(out/(name+'.log'))))
 # The geometry receipt contains runtime; compare the actual objects while preserving both originals.
 oldgeo=read(ROOT/'reference-bit/GEOMETRY.json');newgeo=read(out/'bit-nine/GEOMETRY.json')
 oldgeo.pop('seconds');newgeo.pop('seconds');assert oldgeo==newgeo
 oldt=json.loads(gzip.decompress((ROOT/'reference-bit/GLOBAL-TEMPLATE.json.gz').read_bytes()));newt=json.loads(gzip.decompress((out/'bit-nine/GLOBAL-TEMPLATE.json.gz').read_bytes()))
 assert oldt.pop('geometry_sha256')==sha(ROOT/'reference-bit/GEOMETRY.json')
 assert newt.pop('geometry_sha256')==sha(out/'bit-nine/GEOMETRY.json')
 assert oldt==newt
 bit=read(out/'bit-nine/COMBINED.json');oldbit=read(ROOT/'reference-bit/COMBINED.json')
 assert bit['bit_coarse']==oldbit['bit_coarse'] and bit['finite']==oldbit['finite']
 price=read(ROOT/'signed25/signed25-donor-screen.json');integration=read(ROOT/'signed25/signed25-integration.json');prior=read(ROOT/'signed25/signed25-assembly.json')
 assert price['profile']==integration['paid_profile'];assert price['candidate_sha256']==integration['candidate_sha256']
 assert bit['finite']['row_coefficient']<20161 and integration['invoice']['row']<20161 and int(bit['finite']['two_level_coefficient'])<1<<30000
 r=load(ROOT/'signed25/refine_candidate.py','refine').refine(Q(price['conditional_component_coarse']),Q(bit['bit_coarse']))
 assert r['kappa']==prior['kappa'] and r['strict_constraints']==prior['strict_constraints']
 saving=Q(r['degraded_bit_saving']);previous=Q(r['bootstrap_chain'][0]);cuts=[]
 def ceilq(x):return -((-x.numerator)//x.denominator)
 for value in r['bootstrap_chain'][1:]:
  z=Q(value);gap=min(saving-z,1-z-saving,1-z-saving*(1-previous),1-saving);assert gap>0
  cutoff=max(1,ceilq(36/gap**2),ceilq(2*(4+(int(bit['finite']['two_level_coefficient'])-1).bit_length())/gap))
  assert Q(cutoff)*gap**2>=36 and Q(cutoff)*gap>=2*(4+(int(bit['finite']['two_level_coefficient'])-1).bit_length())
  cuts.append(dict(gap=str(gap),log2_cutoff=str(cutoff)));previous=z
 assert cuts==prior['finite_bootstraps']
 assert inventory(ROOT)==dict(manifest,**{'MANIFEST.json':sha(ROOT/'MANIFEST.json')})
 result=dict(status='PASS_OFFLINE_BIT_SOURCE_CLOSURE_AND_FRESH_RELATIVE_INTEGRATION',source_files=len(pins['bit_files']),input_manifest_sha256=sha(ROOT/'MANIFEST.json'),stages=steps,template_sha256=read(out/'bit-nine/GLOBAL.json')['template_sha256'],bit_coarse=bit['bit_coarse'],complex_coarse=r['complex_coarse'],kappa=r['kappa'],strict_constraints=len(r['strict_constraints']),finite_bootstraps=cuts,negative_controls_rejected=r['negative_controls_rejected'],semantic_template_matches_retained=True,scope='Fresh compressed bit geometry, word, independent audit, finite price and PR396 assembly from complete pinned bit sources. PR370 local record/native receipts and PR377 complex receipts are explicitly reused. No fresh historical full pipelines, all-source proof, Lean, unconditional theorem or ready claim.')
 (out/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa'],flush=True)
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed=steps),indent=2)+'\n');raise
