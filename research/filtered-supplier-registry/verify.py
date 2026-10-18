"""Offline replay of the filtered-response / exact-saturation construction."""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
TEXT={'.py','.json','.md','.txt','.sh','.lean','.cpp','.h','.yml','.yaml','.toml'}
def textfile(p):return p.suffix.lower()in TEXT or p.name in {'LICENSE','NOTICE'}
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def dump(p,z):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 if not __debug__:raise SystemExit('Assertions must be enabled; do not use -O.')
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parent;w=a.work.resolve();assert not w.exists()and root not in w.parents
 manifest=read(root/'MANIFEST.json');expected=read(root/'EXPECTED.json')
 assert manifest['format']=='sha256-lf-text-v1'
 for rel,z in manifest['files'].items():
  p=(root/rel).resolve();assert root in p.parents
  b=p.read_bytes();b=b.replace(b'\r\n',b'\n')if z['mode']=='lf-text'else b
  assert hashlib.sha256(b).hexdigest()==z['sha256'],('input changed',rel)
 started=time.monotonic();w.mkdir(parents=True);src=w/'source';shutil.copytree(root,src)
 for p in src.rglob('*'):
  if p.is_file()and textfile(p):p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
 v=src/'vendor/pr531';stages=[]
 def run(name,script,*args):
  t=time.monotonic();log=w/(name+'.log')
  env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1')
  with log.open('w',encoding='utf-8')as f:
   z=subprocess.run([sys.executable,'-B',str(src/'code/run_portable.py'),str(script),*map(str,args)],stdout=f,stderr=subprocess.STDOUT,env=env)
  stages.append(dict(name=name,seconds=time.monotonic()-t,exit=z.returncode));dump(w/'STAGES.json',stages)
  if z.returncode:print(log.read_text(encoding='utf-8'),file=sys.stderr);raise SystemExit(name+' failed')
  print('PASS',name,round(stages[-1]['seconds'],2),flush=True)
 run('construct-filtered',src/'code/build_filtered.py','--work',w/'constructed')
 run('observation-retarget',src/'code/rewrite_observation.py','--input',w/'constructed/FULL-WORD.json.gz','--out',w/'retargeted')
 localroot=w/'registry';localroot.mkdir()
 for name,raw in [('filtered',w/'constructed/FULL-WORD.json.gz'),('retargeted',w/'retargeted/FULL-WORD.json.gz')]:
  d=localroot/name
  run(name+'-scalar-frames',v/'code/audit_and_transport.py','--raw',raw,'--routing',v/'inputs/data-base/split-centres/CANONICAL-WORD.json.gz','--out',d)
  shutil.copyfile(raw,d/'FULL-WORD.json.gz')
  run(name+'-exact-phases',v/'code/phases_delta.py','--local',d,'--baseline',v/'evidence/local','--compiler',v/'vendor/clifford')
  run(name+'-wrappers',v/'code/adapters_local.py',d/'CANONICAL-WORD.json.gz',d/'RESIDUAL-ADAPTERS.json',d/'WRAPPER-CHECKS.json')
  run(name+'-emission',v/'code/emit_local.py',d)
  run(name+'-independent-local',v/'code/audit_local.py',d)
 selection=['filtered'if i%2==0 else'retargeted'for i in range(72)]
 registry=localroot/'REGISTRY.json';dump(registry,dict(variants={'filtered':'filtered','retargeted':'retargeted'},selection=selection))
 dump(w/'RESOURCE-PROFILE.json',{'local_profile_after':read(localroot/'filtered/LOCAL-CHECKS.json')['forward']['paid_profile']})
 run('universal-resource-calculus',src/'code/audit_uniform_resource.py',v/'inputs/OWNER-PLAN.json',w/'constructed/FULL-WORD.json.gz',src/'inputs/OWNER-PLAN.json',src/'inputs/OWNERS.json.gz',w/'RESOURCE-PROFILE.json',w/'RESOURCE-AUDIT.json')
 # Same width signature; concrete selections are bound to every physical role.
 plan=read(src/'inputs/OWNER-PLAN.json');roles=read(src/'inputs/OWNERS.json.gz')
 for z in roles:z['provider']=selection[z['time']]
 plan['provider_widths']={};plan['provider_profiles']={}
 for name in ('filtered','retargeted'):
  can=read(localroot/name/'CANONICAL-WORD.json.gz');checks=read(localroot/name/'LOCAL-CHECKS.json')
  widths=[9-len(can['frames'][f])for f in can['start'][224:]]
  assert widths==plan['baseline_widths']
  plan['provider_widths'][name]=widths;plan['provider_profiles'][name]=checks['forward']['paid_profile']
 dump(w/'OWNER-PLAN.json',plan)
 rolebytes=gzip.compress(json.dumps(roles,sort_keys=True,separators=(',',':')).encode(),compresslevel=9,mtime=0)
 rolebytes=rolebytes[:9]+b'\xff'+rolebytes[10:];(w/'OWNERS.json.gz').write_bytes(rolebytes)
 run('bind-controller',v/'code/prepare_supplier_base.py','--data-base',v/'inputs/data-base','--local',localroot/'filtered','--out',w/'base')
 run('emit-registry-owners',src/'code/emit_supplier_meta.py','--base',w/'base','--registry',registry,'--owners',w/'OWNERS.json.gz','--plan',w/'OWNER-PLAN.json','--out',w/'hosted')
 audit=w/'audit';audit.mkdir()
 run('independent-registry-owners',src/'code/audit_supplier_meta.py',w/'base',w/'hosted',audit/'ASYNC-AUDIT.json','--registry',registry,'--mutation-controls')
 run('finite-invoice',src/'code/invoice_meta.py','--base',w/'base','--registry',registry,'--hosted',w/'hosted','--audit',audit,'--out',audit,'--retained-invoice',v/'inputs/PR523-PREFIX-AND-INVOICE.json')
 run('exact-assembly',v/'code/assemble.py',audit,w/'base',w/'hosted',v/'inputs/PR493-EXPECTED.json')
 answer=read(audit/'EXACT-ASSEMBLY.json');owners=read(audit/'OWNERS-AND-PROFILE.json');invoice=read(audit/'PREFIX-AND-INVOICE.json')
 result=dict(status='PASS_FILTERED_RESPONSE_META_CONSTRUCTION',kappa=answer['kappa'],kappa_decimal=answer['kappa_decimal'],complex_lower=answer['complex_lower'],bit_lower=answer['bit_lower'],template_sha256=answer['complex_template_sha256'],global_profile=owners['paid_profile'],global_prefix_bits=invoice['global_prefix_bits'],stages=stages,elapsed_seconds=time.monotonic()-started,scope=answer['scope'])
 for key in ('kappa','complex_lower','bit_lower','template_sha256','global_profile','global_prefix_bits'):assert result[key]==expected[key],('frozen result mismatch',key)
 assert len(answer['strict_outer_constraints'])==47
 dump(w/'RESULT.json',result);print(json.dumps({k:result[k]for k in ('status','kappa_decimal','elapsed_seconds')}),flush=True)
if __name__=='__main__':main()
