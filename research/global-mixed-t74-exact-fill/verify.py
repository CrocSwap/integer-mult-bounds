"""Portable finite admission. Fresh native suppliers by default; explicit bound reuse supported."""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--base-native-from',type=Path);ap.add_argument('--extra-native-from',type=Path);a=ap.parse_args();work=a.work.resolve();assert __debug__ and not work.exists() and not work.is_relative_to(P)
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins=rd(P/'MANIFEST.json');actual={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and p!=P/'MANIFEST.json'};assert actual==set(pins)
for rel,h in pins.items():assert sha(P/rel)==h,rel
work.mkdir();(work/'tmp').mkdir();env=dict(os.environ,TMPDIR=str(work/'tmp'),PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
for k in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(k,None)
stages=[]
def run(name,script,*args):
 t=time.monotonic();log=work/(name+'.log')
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT)
 stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(stages,indent=2));assert r.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
old=P/'vendor/pr1297'
# The pinned input witness must be the exact retained predecessor, not merely a similar profile.
for n in ['PLAN.json','OWNERS.json.gz','GLOBAL-TEMPLATE.json.gz','DISPATCH.json','SPEC.json']:assert rd(P/'inputs'/n)==rd(old/n),n
opts=[]
for key,path in [('base',a.base_native_from),('extra',a.extra_native_from)]:
 if path:opts.extend(['--'+key+'-native-from',path.resolve()])
run('retained-provider-and-parent-admission',old/'verify.py','--work',work/'parent',*opts)
pr=rd(work/'parent/RESULT.json');assert pr['status']=='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION' and pr['kappa']==rd(old/'CLAIM.json')['kappa']
run('reconstruct-owners',P/'reconstruct.py','--out',work/'rebuilt-owners')
for n in ['OWNERS.json.gz','ORDER.json','DISPATCH.json','PROFILE.json']:assert rd(work/'rebuilt-owners'/n)==rd(P/n),n
run('lift-parent',P/'lift_parent.py','--owners',work/'rebuilt-owners','--out',work/'rebuilt-parent')
for n in ['GLOBAL-TEMPLATE.json.gz','PLAN.json','CONSTRUCTION.json']:assert rd(work/'rebuilt-parent'/n)==rd(P/n),n
assert rd(work/'rebuilt-parent/SPEC.json')['geometry']==rd(P/'SPEC.json')['geometry']
layout=work/'parent/layout';runtime=layout/'packing74';runtime.mkdir();data=runtime/'candidate';data.mkdir()
for n in ['replay.py','freeze_spec.py','audit_mixed.py','independent_core.py','geometry_controls.py']:shutil.copy2(P/n,runtime/n)
for n in ['code','construction']:shutil.copytree(P/n,runtime/n)
(runtime/'inputs').mkdir();shutil.copy2(P/'inputs/PR589-EXPECTED.json',runtime/'inputs/PR589-EXPECTED.json')
for n in ['PLAN.json','SPEC.json','PROFILE.json','OWNERS.json.gz','DISPATCH.json','CONSTRUCTION.json','GLOBAL-TEMPLATE.json.gz']:shutil.copy2(P/n,data/n)
shutil.copytree(layout/'globalmix51/native-extra',runtime/'native-extra')
base=a.base_native_from.resolve() if a.base_native_from else work/'parent/native-base'
run('strict-t74',runtime/'replay.py','--data',data,'--work',work/'strict','--local',base/'local')
run('geometry-controls',runtime/'geometry_controls.py','--source',layout/'joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold','--strict',work/'strict','--out',work/'GEOMETRY-CONTROLS.json')
r=rd(work/'strict/RESULT.json');assert r['status']=='PASS_STRICT_MIXED_T74_EXACT_FILL' and r['kappa']==rd(P/'CLAIM.json')['kappa'];assert len(rd(work/'GEOMETRY-CONTROLS.json')['rejected'])==6
result=dict(status='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION',kappa=r['kappa'],kappa_decimal=r['kappa_decimal'],manifest_sha256=sha(P/'MANIFEST.json'),native_reuse=dict(base=bool(a.base_native_from),extra=bool(a.extra_native_from)),provider_verification=pr['status'],roles=r['independent']['roles'],prefix_bits=r['independent']['prefix_bits'],charged_prefix_bits=r['independent']['charged_prefix_bits'],physical_row_coefficient=r['independent']['physical_row_coefficient'],row_limit=r['independent']['row_limit'],controls=dict(admission=114,bit=12,controller=15,independent_owner=8,geometry=6),stages=stages,scope=rd(P/'CLAIM.json')['scope'])
(work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal'],flush=True)
